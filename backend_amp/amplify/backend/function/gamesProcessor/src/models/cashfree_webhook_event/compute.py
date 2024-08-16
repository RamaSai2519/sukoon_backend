from bson import ObjectId
from models.interfaces import CashfreeWebhookEventInput as Input, Output
from models.constants import OutputStatus
from db.users import get_user_collection, get_user_payment_collection

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input

    def update_user_membership_status(self):
        customer_details = self.payment_data.get("customer_details")
        phone_number = customer_details.get("customer_phone")
        user_collection = get_user_collection()
        user = user_collection.find_one({"phoneNumber": phone_number})
        if not user:
            return None, ""
        user_id = user.get("_id")
        user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"isPaidUser": True}},
        )
        return True, ""


    def update_payment_status(self):
        order_details = self.payment_data.get("order")
        order_id = order_details.get("order_id")
        payment_details = self.payment_data.get("payment")
        payment_status = payment_details.get("payment_status")
        payment_collection = get_user_payment_collection()
        payment = payment_collection.find_one({"order_id": order_id})
        if not payment:
            return None , ""
        payment_id = payment.get("_id")
        payment_collection.update_one(
            {"_id": ObjectId(payment_id)},
            {"$set": {"payment_status": payment_status}},
        )
        return True, payment_status

    
    def compute(self):

        self.payment_data = self.input.data
        response , payment_status = self.update_payment_status()
        if payment_status == "SUCCESS":
            self.update_user_membership_status()

        return Output(
            output_details= {},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully updated payment status"
        )