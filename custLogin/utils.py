import os
import requests
from custLogin.models import Cryptocurrency

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY")
HUGGINGFACE_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")

def update_crypto_prices():
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

def fetch_crypto_news(crypto_name):
    url = (
        f"https://newsapi.org/v2/everything?q={crypto_name}&language=en&sortBy=publishedAt&pageSize=5&apiKey={NEWSAPI_KEY}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("articles", [])
    return []

def summarize_text(text):
    url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
    }
    payload = {
        "inputs": text,
        "parameters": {"max_length": 100, "min_length": 30, "do_sample": False},
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]["summary_text"]
    return "⚠️ Could not summarize at the moment."
