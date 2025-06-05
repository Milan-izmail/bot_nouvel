import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()
MONOBANK_TOKEN = os.getenv("MONOBANK_TOKEN")

def create_payment_url(amount_uah: int, label: str = "Оплата замовлення") -> str:
    invoice_id = str(uuid.uuid4())
    url = "https://api.monobank.ua/api/merchant/invoice/create"

    headers = {
        "X-Token": MONOBANK_TOKEN,
        "Content-Type": "application/json"
    }

    data = {
        "amount": amount_uah * 100,
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": invoice_id,
            "destination": label
        },
        "redirectUrl": "https://t.me/nouvelpassage",
        "webHookUrl": "",
        "validity": 86400
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json().get("pageUrl", "❌ Посилання не отримано")
    else:
        print("❌ MONOBANK ERROR:", response.status_code, response.text)
        return "https://t.me/nouvelpassage"
