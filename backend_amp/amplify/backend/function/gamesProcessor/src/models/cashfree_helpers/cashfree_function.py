import json
import requests
from shared.configs import CONFIG as config

CASHFREE_CONFIG = config.CASHFREE_API_CREDENTIALS


def get_cashfree_payment_session_id(customer_details_dict, order_details_dict):

    phone_number = customer_details_dict.get("phone_number")
    customer_id = customer_details_dict.get("customer_id")
    customer_name = customer_details_dict.get("customer_name")
    order_id = order_details_dict.get("order_id")
    order_amount = order_details_dict.get("order_amount")

    url = CASHFREE_CONFIG.get("API_URL")

    payload = json.dumps({
        "customer_details": {
            "customer_id": customer_id,
            "customer_phone": phone_number,
            "customer_name": customer_name,
        },
        "order_meta": {
            "return_url": "https://www.sukoonunlimited.com"
        },
        "order_id": order_id,
        "order_currency": "INR",
        "order_amount": order_amount
    })
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'x-api-version': '2023-08-01',
        'x-client-id': CASHFREE_CONFIG.get("APP_ID"),
        'x-client-secret': CASHFREE_CONFIG.get("SECRET_KEY")
    }

    print(headers, url)

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return response
