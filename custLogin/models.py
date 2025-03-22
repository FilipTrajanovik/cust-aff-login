from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    def __str__(self):
        return self.username


class Customer(models.Model):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=500)
    address = models.CharField(max_length=500)

    username = models.CharField(max_length=500)
    password = models.CharField(max_length=128)
    raw_password = models.CharField(max_length=128, blank=True, null=True)

    balance = models.IntegerField(default=1000.0)
    manager = models.ForeignKey(ManagerProfile, on_delete=models.CASCADE)

    can_cashout = models.BooleanField(default=False)
    payout_date = models.DateField(blank=True, null=True)

    credit_card_number = models.CharField(max_length=19, blank=True, null=True)
    credit_card_expiry = models.CharField(max_length=5, blank=True, null=True)
    credit_card_cvc = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.email}. Total for cashing out: {self.balance}"
