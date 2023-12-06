from django.db import models
from django.contrib.auth.models import User


class AvailableBookingDate(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.start}:{self.end}"







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


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return str(self.title)