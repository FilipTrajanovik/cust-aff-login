from celery import shared_task

from custLogin.models import Cryptocurrency
import requests


@shared_task
def debug_task():
    print("✅ Debug task ran!")
    return "OK"

@shared_task
def update_all_crypto_prices():
    updated = []
    cryptos = Cryptocurrency.objects.all()
    for crypto in cryptos:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto.coingecko_id}&vs_currencies=usd"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            price = data.get(crypto.coingecko_id, {}).get("usd")
            if price is not None:
                crypto.value_usd = price
                crypto.save()
                updated.append((crypto.name, price))
    return updated