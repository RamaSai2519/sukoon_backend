from models.interfaces import UserReferralInput as Input, Output
from models.constants import OutputStatus
import random
import string
from db.referral import get_user_referral_collection
from db.users import get_user_collection

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input
 
    def _generate_referral_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def _add_referral(self, referred_user_id, user_id, level):
        referrals_collection = get_user_referral_collection()
        referral = {
            "userId": user_id,
            "referredUserId": referred_user_id,
            "level": level,
        }
        referrals_collection.insert_one(referral)
        
        referrer = self.users_collection.find_one({"_id": user_id})
        if referrer and referrer.get("referredBy"):
            parent_referrer = self.users_collection.find_one({"referralCode": referrer["referredBy"]})
            if parent_referrer:
                self._add_referral(referred_user_id, parent_referrer["_id"], level + 1)


    def _register(self):
        referral_code = self.input.referral_code
        referrer = self.users_collection.find_one({"referralCode": referral_code})

        phone_number = self.input.phone_number
        user = self.users_collection.find_one({"phoneNumber": phone_number})
        if user:
            return "Successfully logged in user"
        
        new_user = {
            "name": self.input.name,
            "city": self.input.city,
            "phoneNumber": self.input.phone_number,
            "referralCode": self._generate_referral_code(),
            "referredBy": referrer["referralCode"] if referrer else None
        }
        new_user_id = self.users_collection.insert_one(new_user).inserted_id

        if referrer:
            self._add_referral(new_user_id, referrer["_id"], 1)
        return "Successfully registered user"

    def compute(self):
        self.users_collection = get_user_collection()
        message = self._register()

        return Output(
            output_details= {},
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )