import requests
from bson import ObjectId
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.models.constants import OutputStatus
from shared.db.referral import get_offers_collection
from shared.db.users import get_meta_collection, get_user_collection
from shared.models.interfaces import RedeemOfferInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.redeemed_offers = []
        self.meta_collection = get_meta_collection()
        self.users_collection = get_user_collection()
        self.offers_collection = get_offers_collection()

    def update_user_meta(self, data: dict) -> dict:
        query = {"user": ObjectId(self.input.user_id)}
        update = {"$set": data}
        self.meta_collection.update_one(query, update)
        return data

    def get_user_meta(self) -> dict:
        query = {"user": ObjectId(self.input.user_id)}
        doc = self.meta_collection.find_one(query)
        if not doc:
            doc = query
            _id = self.meta_collection.insert_one(doc).inserted_id
            doc["_id"] = ObjectId(_id)
        self.redeemed_offers = doc.get("redeemed_offers", [])
        return doc

    def prep_data(self, data: dict) -> dict:
        self.redeemed_offers.append(self.input.couponCode)
        data["redeemed_offers"] = self.redeemed_offers
        return data

    def validate_offer(self) -> tuple:
        if self.input.couponCode in self.redeemed_offers:
            return False, "Offer already redeemed"

        return True, ""

    def get_user(self) -> dict:
        query = {"_id": ObjectId(self.input.user_id)}
        return self.users_collection.find_one(query)

    def get_offer(self) -> dict:
        query = {"couponCode": self.input.couponCode}
        return self.offers_collection.find_one(query)

    def send_whatsapp(self):
        url = config.URL + '/actions/send_whatsapp'
        user = self.get_user()
        offer = self.get_offer()

        user_phone = user.get("phoneNumber")
        expiry_date = offer.get("validTill")
        expiry_date = expiry_date.strftime(
            "%d %B, %Y") if expiry_date else "Not provided"

        payload = {
            "phone_number": user_phone,
            "template_name": "PARTNER_POST_SUBSCRIPTION",
            "parameters": {
                "user_name": user.get("name", user_phone),
                "offer_title": offer.get("title"),
                "website_url": offer.get("website"),
                "expiry_date": expiry_date,
                "phone_number": "+918660610840"
            }
        }

        response = requests.post(url, json=payload)
        response_dict = response.json()
        status = response_dict.get("output_status")
        failed_message = False, "Failed to send WA message"
        if not status:
            return failed_message
        if status == OutputStatus.FAILURE:
            return failed_message
        return True, "Successfully sent WA message"

    def compute(self) -> Output:
        user_meta = self.get_user_meta()
        valid_offer, error_message = self.validate_offer()
        if not valid_offer:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message=error_message
            )

        wa_status, wa_message = self.send_whatsapp()
        if not wa_status:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message=wa_message
            )

        new_data = self.prep_data(user_meta)
        self.update_user_meta(new_data)

        return Output(
            output_details=Common.jsonify(new_data),
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully redeemed offer" + " and " + wa_message
        )
