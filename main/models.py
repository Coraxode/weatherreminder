from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=50)
    current_weather = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    notification_period = models.FloatField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.city}, notification period: {self.notification_period} hours."


class UserSubscriptions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscriptions = models.ManyToManyField(Subscription, blank=True)

    def __str__(self):
        return f"{self.user}'s subscriptions"
