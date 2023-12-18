from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.db.models.signals import post_save


class AvailableBookingDate(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.start.strftime('%H:%M %d/%m/%Y')} - {self.end.strftime('%H:%M %d/%m/%Y')}"


class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    bookingPerson = models.ForeignKey(User, on_delete=models.CASCADE)
    availableBookingDate = models.ForeignKey(AvailableBookingDate, on_delete=models.CASCADE)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    isAccepted = models.BooleanField(default=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return str(self.title)

# class Events(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=255, null=True, blank=True)
#     start = models.DateTimeField(null=True, blank=True)
#     end = models.DateTimeField(null=True, blank=True)
#
#     def __str__(self):
#         return f"{self.name} {self.start}:{self.end}"
#
#     class Meta:
#         db_table = "tblevents"
