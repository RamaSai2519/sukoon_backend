import json
import requests
import random
from datetime import datetime
from bson import ObjectId
from db.events import get_events_collection
from models.constants import OutputStatus, application_json_header
from db.users import get_user_collection, get_user_payment_collection
from models.interfaces import CashfreeWebhookEventInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.headers = application_json_header

    def get_user_id_from_number(self):
        customer_details = self.payment_data.get("customer_details")
        phone_number = customer_details.get("customer_phone")
        user_collection = get_user_collection()
        user = user_collection.find_one({"phoneNumber": phone_number})
        if not user:
            return None, ""
        user_id = user.get("_id")

        return user_id

    def update_user_membership_status(self):
        user_collection = get_user_collection()
        user_collection.update_one(
            {"_id": ObjectId(self.user_id)},
            {"$set": {"isPaidUser": True}},
        )
        return True, ""

    def send_invoice_to_the_user(self, invoice_s3_url, event_id):
        customer_details = self.payment_data.get("customer_details")
        phone_number = customer_details.get("customer_phone")

        url = "https://6x4j0qxbmk.execute-api.ap-south-1.amazonaws.com/main/actions/send_whatsapp"

        if event_id:
            event_config_collection = get_events_collection()
            event = event_config_collection.find_one(
                {"_id": ObjectId(event_id)})
            event_name = event.get("mainTitle")

            payload = json.dumps({
                "phone_number": phone_number,
                "template_name": "EVENT_INVOICE",
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
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

    def get_invoice_s3_url(self, payment_amount):
        customer_details = self.payment_data.get("customer_details")
        customer_name = customer_details.get("customer_name")
        invoice_number = str(random.randint(1000, 9999))

        url = "https://mark.sukoonunlimited.com/invoice"
        rate = payment_amount/1.18

        payload = {
            "rate": round(rate, 2),
            "sgst": round(rate * .09, 2),
            "cgst": round(rate * .09, 2),
            "amount": payment_amount,
            "userId": str(self.user_id),
            "invoiceNumber": invoice_number,
            "customerFullName": customer_name,
            "itemDescription": "Club Sukoon Annual Membership",
            "createdDate": datetime.today().strftime('%Y-%m-%d')
        }

        response = requests.request(
            "POST", url, headers=self.headers, data=json.dumps(payload))

        json_response = Output(**response.json())
        data = json_response.output_details
        s3_url = data.get("file_url")
        return s3_url, invoice_number

    def update_payment_status(self):

        order_details = self.payment_data.get("order")
        order_id = order_details.get("order_id")
        payment_details = self.payment_data.get("payment")
        payment_amount = payment_details.get("payment_amount")
        payment_status = payment_details.get("payment_status")
        invoice_number = "invoice not generated"
        invoice_s3_url = ""
        payment_collection = get_user_payment_collection()
        payment = payment_collection.find_one({"order_id": order_id})
        event_id = payment.get("event_id")

        if payment_status == "SUCCESS":
            invoice_s3_url, invoice_number = self.get_invoice_s3_url(
                payment_amount)
            self.send_invoice_to_the_user(invoice_s3_url, event_id)

        if not payment:
            return None, ""
        payment_id = payment.get("_id")
        payment_collection.update_one(
            {"_id": ObjectId(payment_id)},
            {"$set": {"payment_status": payment_status,
                      "invoice_number": invoice_number, "invoice_link": invoice_s3_url}},
        )
        return True, payment_status, int(payment_amount)

    def compute(self):

        self.payment_data = self.input.data
        self.user_id = self.get_user_id_from_number()
        response, payment_status, payment_amount = self.update_payment_status()
        if payment_status == "SUCCESS" and payment_amount == 999:
            self.update_user_membership_status()

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully updated payment status"
        )
