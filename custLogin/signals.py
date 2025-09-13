from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer, Cryptocurrency, UserWallet


@receiver(post_save, sender=Customer)
def create_wallet_for_customer(sender, instance, created, **kwargs):
    print(f"Signal triggered for customer: {instance.username}, created: {created}")

    if created:
        cryptos = Cryptocurrency.objects.all()
        print(f"Found {cryptos.count()} cryptocurrencies")

        for crypto in cryptos:
            if crypto.coingecko_id == 'bitcoin':
                balance = instance.balance / crypto.value_usd if crypto.value_usd else 0
            else:
                balance = 0

            wallet = UserWallet.objects.create(
                customer=instance,
                cryptocurrency=crypto,
                balance=balance,
            )
            print(f"Created {crypto.name} wallet with balance {balance}")