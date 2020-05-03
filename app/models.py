from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=12)

    def __str__(self):
        return self.phone


class Route(models.Model):
    origin = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    first_class_cost = models.CharField(max_length=10)
    economy_class_cost = models.CharField(max_length=10)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.origin + "-" + self.destination


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, null=True, on_delete=models.SET_NULL)
    travelling_datetime = models.DateTimeField()
    seats = ArrayField(models.IntegerField())
    amount = models.IntegerField()
    paid = models.BooleanField(default=False)
    booking_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
