import json
import random
import requests
from bson import ObjectId
from datetime import datetime
from shared.configs import CONFIG as config
from shared.db.users import get_user_collection, get_user_payment_collection
from shared.models.interfaces import CashfreeWebhookEventInput as Input, Output
from shared.db.events import get_events_collection, get_contribute_events_collection
from shared.models.constants import OutputStatus, application_json_header, pay_types


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.event = None
        self.phoneNumber = None
        self.headers = application_json_header
        self.events_collection = get_events_collection()
        self.payments_collection = get_user_payment_collection()
        self.contribute_events_collection = get_contribute_events_collection()

    def get_user_id_from_number(self) -> str:
        customer_details = self.payment_data.get("customer_details")
        self.phoneNumber = customer_details.get("customer_phone")
        user_collection = get_user_collection()
        user = user_collection.find_one({"phoneNumber": self.phoneNumber})
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

    def send_invoice_to_the_user(self, invoice_s3_url: str, event_name: str = None):
        customer_details = self.payment_data.get("customer_details")
        phone_number = customer_details.get("customer_phone")

        url = config.URL + "/actions/send_whatsapp"
        if event_name:
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

        print(response.text, "invoice_response_cashfree")

    def generate_invoice(self, payment_amount: int, description: str) -> tuple:
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
            "itemDescription": description,
            "invoiceNumber": invoice_number,
            "customerFullName": customer_name,
            "createdDate": datetime.today().strftime('%Y-%m-%d')
        }

        response = requests.request(
            "POST", url, headers=self.headers, data=json.dumps(payload))

        if "output_details" in response.json():
            json_response = Output(**response.json())
            data = json_response.output_details
            s3_url = data.get("file_url")
        else:
            file_name = f"{self.user_id}-{invoice_number}.pdf"
            s3_url = "https://s3.ap-south-1.amazonaws.com/sukoon-media/invoices/" + file_name
        return s3_url, invoice_number

    def get_event(self, event_id: str) -> dict:
        event = self.events_collection.find_one({"slug": event_id})
        if not event:
            event = self.contribute_events_collection.find_one(
                {"slug": event_id})
            if not event:
                return None
        return event

    def determine_description(self, pay_type: str, event_id: str):
        if pay_type == "event":
            self.event = self.get_event(event_id)
            return self.event.get("mainTitle")
        for pay in pay_types:
            if pay.get("type") == pay_type:
                return pay.get("desc")
        return "Invoice"

    def register_user_for_event(self, event_id: str):
        url = config.URL + "/actions/upsert_event_user"
        payload = {'phoneNumber': self.phoneNumber,
                   'isUserPaid': True, 'source': event_id}
        response = requests.post(url, json=payload)
        response_dict = response.json()
        message = "User not registered for event"
        if "output_status" in response_dict and response_dict.get("output_status") == "SUCCESS":
            message = "User registered for event"
        return message

    def send_event_details(self) -> str:
        url = config.URL + "/actions/send_whatsapp"
        payload = {
            'phone_number': self.phoneNumber,
            'template_name': 'EVENT_REGISTRATION_CONFIRMATION',
            'parameters': {
                'user_name': self.payment_data.get("customer_details").get("customer_name"),
                'topic_name': self.event.get("mainTitle"),
                'date_and_time': self.event.get("startEventDate", "").strftime('%d %b %Y %H:%M'),
                'custom_text': self.event.get("subTitle"),
                'speakers_name': self.event.get("guestSpeaker"),
                'event_name': self.event.get("mainTitle"),
                'image_link': self.event.get("imageUrl"),
                'webinar_link': self.event.get("meetingLink"),
                'phone_number': "+918660610840",
                'whatsapp_community_link': "https://sukoonunlimited.com/wa-join-community"
            }
        }
        response = requests.post(url, json=payload)
        response_dict = response.json()
        if "output_status" in response_dict and response_dict.get("output_status") == "SUCCESS":
            return "Event details sent"
        print(response_dict)
        return "Event details not sent"

    def update_payment_status(self) -> tuple:

        order_details = self.payment_data.get("order")
        order_id = order_details.get("order_id")
        payment_details = self.payment_data.get("payment")
        payment_amount = payment_details.get("payment_amount")
        payment_status = payment_details.get("payment_status")
        invoice_number = "invoice not generated"
        invoice_s3_url = ""
        payment = self.payments_collection.find_one({"order_id": order_id})
        if not payment:
            return None, ""

        event_id = payment.get("event_id")
        pay_type = payment.get("pay_type")

        if payment_status == "SUCCESS":
            description = self.determine_description(pay_type, event_id)
            invoice_s3_url, invoice_number = self.generate_invoice(
                payment_amount, description)
            if pay_type == "event":
                self.send_invoice_to_the_user(invoice_s3_url, description)
                register_message = self.register_user_for_event(event_id)
                print(register_message, "register_message_cashfree")
                event_wa_message = self.send_event_details()
                print(event_wa_message, "event_wa_message_cashfree")
            else:
                if pay_type in ['code', 'club']:
                    self.update_user_membership_status()
                    if pay_type == 'code':
                        self.update_user_meta(event_id)
                self.send_invoice_to_the_user(invoice_s3_url)

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
        self.update_payment_status()

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully updated payment status"
        )
