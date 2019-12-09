from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=12)

    def __str__(self):
        return self.phone


class Route(models.Model):
    origin = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    cost = models.CharField(max_length=10)

    def __str__(self):
        return self.origin + "-"+ self.destination


class Booking(models.Model):
    name = models.CharField(max_length=100)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    seats = models.IntegerField()
    amount = models.IntegerField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


