import json
import random
import requests
from bson import ObjectId
from datetime import datetime
from shared.configs import CONFIG as config
from shared.db.events import get_events_collection
from shared.models.constants import OutputStatus, application_json_header
from shared.db.users import get_user_collection, get_user_payment_collection
from shared.models.interfaces import CashfreeWebhookEventInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.headers = application_json_header
        self.events_collection = get_events_collection()
        self.payments_collection = get_user_payment_collection()

    def get_user_id_from_number(self) -> str:
        customer_details = self.payment_data.get("customer_details")
        phone_number = customer_details.get("customer_phone")
        user_collection = get_user_collection()
        user = user_collection.find_one({"phoneNumber": phone_number})
        if not user:
            return None
        user_id = user.get("_id")

        return user_id

    def update_user_membership_status(self):
        user_collection = get_user_collection()
        user_collection.update_one(
            {"_id": ObjectId(self.user_id)},
            {"$set": {"isPaidUser": True}},
        )
        return True, ""

    def send_invoice_to_the_user(self, invoice_s3_url, event_name):
        customer_details = self.payment_data.get("customer_details")
        phone_number = customer_details.get("customer_phone")

        url = config.URL + "/actions/send_whatsapp"
        if event_name:
            print("Event name is present")
            payload = json.dumps({
                "phone_number": phone_number,
                "template_name": "EVENT_INVOICE_GENERIC",
                "parameters": {
                    "event_name": event_name,
                    "document_link": invoice_s3_url
                }
            })
        else:
            payload = json.dumps({
                "phone_number": phone_number,
                "template_name": "INVOICE_DOWNLOAD",
                "parameters": {
                    "document_link": invoice_s3_url
                }
            })
        headers = self.headers
        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

    def generate_invoice(self, payment_amount, payment_type):
        customer_details = self.payment_data.get("customer_details")
        customer_name = customer_details.get("customer_name")
        invoice_number = str(random.randint(1000, 9999))

        url = config.MARK_URL + "/quart/invoice"
        rate = payment_amount/1.18

        payload = {
            "rate": round(rate, 2),
            "sgst": round(rate * .09, 2),
            "cgst": round(rate * .09, 2),
            "amount": payment_amount,
            "userId": str(self.user_id),
            "invoiceNumber": invoice_number,
            "customerFullName": customer_name,
            "itemDescription": payment_type or "Event Payment",
            "createdDate": datetime.today().strftime('%Y-%m-%d')
        }

        response = requests.request(
            "POST", url, headers=self.headers, data=json.dumps(payload))

        json_response = Output(**response.json())
        data = json_response.output_details
        s3_url = data.get("file_url")
        return s3_url, invoice_number

    def get_payment_type(self, event_id: str, pay_type: str) -> tuple:
        if pay_type == "event":
            event = self.events_collection.find_one({"slug": event_id})
            if not event:
                return None, "event"
            event_name = event.get("mainTitle")
            return event_name, "event"
        else:
            return None, pay_type

    def update_payment_status(self):

        order_details = self.payment_data.get("order")
        order_id = order_details.get("order_id")
        payment_details = self.payment_data.get("payment")
        payment_amount = payment_details.get("payment_amount")
        payment_status = payment_details.get("payment_status")
        invoice_number = "invoice not generated"
        invoice_s3_url = ""
        payment = self.payments_collection.find_one({"order_id": order_id})
        event_id = payment.get("event_id")
        pay_type = payment.get("pay_type", "club")
        event_name, pay_type = self.get_payment_type(event_id, pay_type)

        if payment_status == "SUCCESS":
            invoice_s3_url, invoice_number = self.generate_invoice(
                payment_amount, event_name)
            self.send_invoice_to_the_user(invoice_s3_url, event_name)

        if not payment:
            return None, ""
        payment_id = payment.get("_id")
        self.payments_collection.update_one(
            {"_id": ObjectId(payment_id)},
            {"$set": {"payment_status": payment_status,
                      "invoice_number": invoice_number, "invoice_link": invoice_s3_url}},
        )
        return payment_status, pay_type, event_id

    def update_user_meta(self, code: str) -> dict:
        payload = {
            "user_id": str(self.user_id),
            "couponCode": code,
            "redeemed": True
        }
        url = config.URL + "/actions/redeem_offer"
        response = requests.post(url, json=payload)
        response_dict = response.json()
        return response_dict

    def compute(self) -> Output:
        self.payment_data = self.input.data
        self.user_id = self.get_user_id_from_number()
        payment_status, pay_type, event_id = self.update_payment_status()
        if payment_status == "SUCCESS" and pay_type != "event":
            self.update_user_membership_status()
            if pay_type == 'code':
                doc = self.update_user_meta(event_id)
                print(doc)

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully updated payment status"
        )
