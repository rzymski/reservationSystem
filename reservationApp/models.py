from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from icecream import ic
from datetime import timedelta
from django.utils import timezone


class AvailableBookingDate(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    intervalTime = models.IntegerField(null=True, blank=True)
    breakBetweenIntervals = models.IntegerField(default=0)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        if self.intervalTime:
            return f"Dostępny termin {self.user} od {self.start.strftime('%H:%M %d/%m/%Y')} do {self.end.strftime('%H:%M %d/%m/%Y')}. Czas wizyty = {self.intervalTime}"
        else:
            return f"Dostępny termin {self.user} od {self.start.strftime('%H:%M %d/%m/%Y')} do {self.end.strftime('%H:%M %d/%m/%Y')}"
    # def __str__(self):
    #     if self.intervalTime:
    #         return f"{self.user} {self.start.strftime('%H:%M %d/%m/%Y')} - {self.end.strftime('%H:%M %d/%m/%Y')} interval={self.intervalTime} break={self.breakBetweenIntervals}"
    #     else:
    #         return f"{self.user} {self.start.strftime('%H:%M %d/%m/%Y')} - {self.end.strftime('%H:%M %d/%m/%Y')}"

    def clean(self):
        if self.start and self.end and self.start >= self.end:
            raise ValidationError("Nie można zatwierdzić terminu. Koniec jest przed startem.", code="EndBeforeStart")
        if self.intervalTime and int(self.intervalTime) > 0:
            helpStartDate = self.start
            helpInterval = timedelta(minutes=int(self.intervalTime))
            helpBreakBetweenIntervals = timedelta(minutes=int(self.breakBetweenIntervals)) if self.breakBetweenIntervals else timedelta(minutes=0)
            condition = False
            while helpStartDate < self.end:
                helpStartDate += helpInterval + helpBreakBetweenIntervals
                if helpStartDate == self.end:
                    condition = True
            if not condition:
                raise ValidationError("Nie można zatwierdzić terminu. Start wraz z czasami pracy nie równa się Końcowi.", code="wrongIntervals")
        # Check consistency with related reservations
        if self.id:
            for reservation in self.reservation_set.filter(isAccepted=True, isDeleted=False):
                if self.intervalTime and int(self.intervalTime) > 0 and ((reservation.end - reservation.start) != timedelta(minutes=(int(self.intervalTime) + int(self.breakBetweenIntervals)))):
                    raise ValidationError(f"Dostepny termin posiada zatwierdzoną rezerwację z innym przedziałem czasowym.", code="durationMismatchWithReservation")
                # Check if the is reservation with bigger range
                if self.start > reservation.start or self.end < reservation.end:
                    raise ValidationError(f"Nie można zatwierdzić terminu. Dostepny termin posiada zatwierdzoną rezerwację z większym zakresem czasowym.", code="existReservationWithBiggerRange")
        # One user could have only one AvailableBookingDate in the same time
        if self.start and self.end and self.user:
            conflictDates = AvailableBookingDate.objects.filter(
                user=self.user,
                start__lt=self.end,
                end__gt=self.start,
                isDeleted=False
            ).exclude(id=self.id)
            if conflictDates.exists():
                raise ValidationError(f"Nie można zatwierdzić terminu. Użytkownik już ma spotkanie w tym czasie.", code="userAlreadyHaveExistingAvailableBookingDateInThisTime")

    def save(self, *args, **kwargs):
        fromUser = kwargs.pop('fromUser', None)
        self.clean()
        super().save(*args, **kwargs)
        for reservation in self.reservation_set.filter(isAccepted=False, isDeleted=False):
            if self.intervalTime and int(self.intervalTime) > 0:
                if (reservation.end - reservation.start) != timedelta(minutes=(int(self.intervalTime)) + int(self.breakBetweenIntervals)):
                    reservation.availableBookingDate = None
                    reservation.save()
                    Notification.createNotification(9, reservation.bookingPerson, fromUser, None, reservation)
            if reservation.end > self.end or reservation.start < self.start:
                reservation.availableBookingDate = None
                reservation.save()
                Notification.createNotification(9, reservation.bookingPerson, fromUser, None, reservation)

    # class Meta:
    #     verbose_name = "Dostępny termin"
    #     verbose_name_plural = "Dostępne terminy"


class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    bookingPerson = models.ForeignKey(User, on_delete=models.CASCADE)
    availableBookingDate = models.ForeignKey(AvailableBookingDate, on_delete=models.CASCADE, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    isAccepted = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        if self.isAccepted:
            return f"Potwierdzona rezerwacja {self.bookingPerson} od {self.start.strftime('%H:%M %d/%m/%Y')} do {self.end.strftime('%H:%M %d/%m/%Y')}"
        else:
            return f"Proponowana rezerwacja {self.bookingPerson} od {self.start.strftime('%H:%M %d/%m/%Y')} do {self.end.strftime('%H:%M %d/%m/%Y')}"

    def clean(self):
        if self.start and self.end and self.start >= self.end:
            raise ValidationError("Nie można zatwierdzić rezerwacji. Data końcowa nie może być przed początkową.")
        conflictingAcceptedReservations = Reservation.objects.filter(
            # availableBookingDate=self.availableBookingDate,
            bookingPerson=self.bookingPerson,
            isAccepted=True,
            start__lt=self.end,
            end__gt=self.start,
            isDeleted=False
        ).exclude(pk=self.pk)  # Exclude self if instance is being updated
        if conflictingAcceptedReservations.exists():
            raise ValidationError("Nie można zatwierdzić rezerwacji. Następuje kolizja terminów. Użytkownik już ma zaakceptowaną rezerwacje w tym terminie", code="conflict")
        if self.isAccepted:
            conflictingNotAcceptedReservations = Reservation.objects.filter(
                bookingPerson=self.bookingPerson,
                isAccepted=False,
                start__lt=self.end,
                end__gt=self.start,
                isDeleted=False
            ).exclude(pk=self.pk)
            for conflictNotAcceptedReservation in conflictingNotAcceptedReservations:
                conflictNotAcceptedReservation.isDeleted = True
                conflictNotAcceptedReservation.save()
        if self.availableBookingDate:
            # Check for mismatch between interval+break and duration time
            if self.availableBookingDate.intervalTime and int(self.availableBookingDate.intervalTime) > 0:
                if self.end - self.start != timedelta(minutes=(int(self.availableBookingDate.intervalTime) + int(self.availableBookingDate.breakBetweenIntervals))):
                    raise ValidationError("Nie można zatwierdzić rezerwacji. Czas rezerwacji nie pokrywa się z przedziałem czasowym dostępnego terminu.", code="durationMismatch")
            # Check if reservation time is in available bookind date range time
            if self.availableBookingDate.end < self.end or self.start < self.availableBookingDate.start:
                raise ValidationError("Nie można zatwierdzić rezerwacji. Zakres rezerwacji przekracza zakres dostępnego terminu.", code="reservationExceedRange")
            # One user could have only one Reservation in the same time
            if self.start and self.end and self.bookingPerson:
                conflictDates = Reservation.objects.filter(
                    bookingPerson=self.bookingPerson,
                    availableBookingDate=self.availableBookingDate,
                    start__lt=self.end,
                    end__gt=self.start,
                    isDeleted=False
                ).exclude(id=self.id)
                if conflictDates.exists():
                    raise ValidationError(f"Nie można dodac rezerwacji. Użytkownik już ma rezerwacje w tym czasie w tym dostepnym terminie.", code="userAlreadyHaveExistingReservationInThisAvailableBookingDateInThisTime")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    age = models.IntegerField(null=True, blank=True)
    UNDEFINED = 'UNDEFINED'
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    SEX_CHOICES = [
        (UNDEFINED, 'Brak'),
        (MALE, 'Mężczyzna'),
        (FEMALE, 'Kobieta'),
    ]
    sex = models.CharField(max_length=30, choices=SEX_CHOICES, null=True, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    profileImage = models.ImageField(default='default.jpg', upload_to='profilePictures')
    #userColor = models.CharField(max_length=20, default="white")

    def __str__(self):
        return f"{self.user.username} {self.user.first_name} {self.user.last_name} {self.age} {self.sex}"

    def save(self):
        super().save()
        img = Image.open(self.profileImage.path)
        img = img.resize((300, 300))
        img.save(self.profileImage.path)


def create_profile(sender, instance, created, **kwargs):
    if created:
        newUserProfile = UserProfile(user=instance)
        newUserProfile.save()


post_save.connect(create_profile, sender=User)


class Notification(models.Model):
    # 0 - potwierdził twoją rezerwacje
    # 1 - zaakceptował twoją propozycje terminu
    # 2 - zaproponował termin rezerwacji
    # 3 - anululował potwierdzony termin rezerwacji
    # 4 - usunął twoją rezerwacje
    # 5 - usunął twoją propozycje terminu
    # 6 - usunął twój dostępny termin
    # 7 - edytował twój dostępny termin
    # 8 - edytował twoją propozycje terminu
    # 9 - edytował swój dostępny termin poza przedział twojej rezerwacji
    id = models.AutoField(primary_key=True)
    notificationType = models.IntegerField()
    toUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_to', null=True)
    fromUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_from', null=True)
    availableBookingDate = models.ForeignKey(AvailableBookingDate, on_delete=models.CASCADE, null=True, blank=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, null=True, blank=True)
    hasBeenSeen = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)
    isDeleted = models.BooleanField(default=False)

    @staticmethod
    def createNotification(notificationType, toUser, fromUser, availableBookingDate=None, reservation=None):
        notification = Notification.objects.create(
            notificationType=notificationType,
            toUser=toUser,
            fromUser=fromUser,
            availableBookingDate=availableBookingDate,
            reservation=reservation,
            hasBeenSeen=False,
            isDeleted=False,
        )
        return notification

    def __str__(self):
        if self.reservation:
            return f"Typ: {self.notificationType} do: {self.toUser} od: {self.fromUser} {self.reservation}"
        elif self.availableBookingDate:
            return f"Typ: {self.notificationType} do: {self.toUser} od: {self.fromUser} {self.availableBookingDate}"
        else:
            return f"Typ: {self.notificationType} do: {self.toUser} od: {self.fromUser}"













class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return str(self.title)

