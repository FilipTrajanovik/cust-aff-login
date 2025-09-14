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


    has_withdrawn = models.BooleanField(default=False)

    is_locked = models.BooleanField(default=False)
    locked_reason = models.TextField(blank=True, null=True)
    locked_at = models.DateField(blank=True, null=True)


    def __str__(self):
        return f"{self.username} - {self.email}. Total for cashing out: {self.balance}"


class Cryptocurrency(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    coingecko_id = models.CharField(max_length=100, null=True, blank=True)
    image_url = models.CharField(max_length=5000, null=True, blank=True)
    value_usd = models.FloatField(null=True, blank=True, default=0)

    def __str__(self):
        return f"{self.name} (${self.value_usd})"


class UserWallet(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='wallets')
    cryptocurrency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

    class Meta:
        unique_together = ('customer', 'cryptocurrency')

    def __str__(self):
        return f"{self.customer.username} - {self.cryptocurrency} - {self.balance}"


class CryptoTransfer(models.Model):
    sender = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='receiver')
    cryptocurrency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.receiver.username} - {self.amount} {self.cryptocurrency} - {self.timestamp}"


class CryptoConvert(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    from_crypto = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, related_name='conversions_from')
    to_crypto = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, related_name='conversions_to')
    amount = models.FloatField(default=0)
    fee = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Set a 10% fee when saving
        self.fee = self.amount * 0.10
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.from_crypto} -> {self.to_crypto}. Fee: {self.fee}"

class ChatRoom(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    manager = models.ForeignKey(ManagerProfile, on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.CharField(max_length=200, default='General Support')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    last_message_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Chat: {self.customer.username} - {self.subject}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender_customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    sender_manager = models.ForeignKey(ManagerProfile, on_delete=models.SET_NULL, blank=True, null=True)
    message=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at',]
