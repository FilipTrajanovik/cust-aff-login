from django.db.models.signals import post_save
from django.dispatch import receiver

from custLogin.models import Customer, Cryptocurrency, UserWallet


@receiver(post_save, sender=Customer)
def create_wallet_for_customer(sender, instance, created, **kwargs):
    if created:
        cryptos = Cryptocurrency.objects.all()
        customer = Customer.objects.filter(pk=instance.pk)
        existing_wallets = UserWallet.objects.filter(customer=instance).values_list('cryptocurrency_id', flat=True)
        for crypto in cryptos:

            if crypto.id in existing_wallets:
                continue

            if crypto.coingecko_id == 'bitcoin':
                balance = instance.balance / crypto.value_usd if crypto.value_usd else 0
            else:
                balance = 0

            UserWallet.objects.create(
                customer=instance,
                cryptocurrency=crypto,
                balance=balance,
            )
