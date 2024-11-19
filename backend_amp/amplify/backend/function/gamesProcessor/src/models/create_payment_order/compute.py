import uuid
from bson import ObjectId
from http import HTTPStatus
from datetime import datetime
from models.constants import OutputStatus
from db.users import get_user_collection, get_user_payment_collection
from models.interfaces import CreatePaymentOrderInput as Input, Output
from models.cashfree_helpers.cashfree_function import get_cashfree_payment_session_id

 
class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input


    def create_user_details_dict(self, user_id) -> dict:
        user_collection = get_user_collection()
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        user_name = user.get("name")
        user_phone_number = user.get("phoneNumber")
        user_details_dict = {
            "customer_id": user_id,
            "customer_name": user_name,
            "phone_number": user_phone_number,
        }
        return user_details_dict
    
    def create_order_details_dict(self) -> dict:
        order_id = str(uuid.uuid4())
        order_amount = self.input.order_amount
        order_details_dict = {
            "order_id": order_id,
            "order_amount": order_amount
        }
        return order_details_dict
    
    def create_payment_object_in_db(self, order_details_dict) -> dict:
        user_payment_collection = get_user_payment_collection()

        order_details_dict = {
            "user_id": self.input.user_id,
            "event_id": self.input.event_id,
            "created_at": datetime.now(),
            "order_id": order_details_dict.get("order_id"),
            "payment_status": "INCOMPLETED",
            "order_amount": self.input.order_amount
        }
        user_payment_collection.insert_one(order_details_dict)

    def compute(self) -> Output:
        
        user_details_dict = self.create_user_details_dict(self.input.user_id)
        order_details_dict = self.create_order_details_dict()

        api_response = get_cashfree_payment_session_id(user_details_dict, order_details_dict)
        if not api_response:
            return Output(
                output_details= {},
                output_status=OutputStatus.FAILURE,
                output_message="Not able to create payment session id"
        )

        response_status_code = api_response.status_code
        if not response_status_code == HTTPStatus.OK.value:
            return Output(
                output_details= {},
                output_status=OutputStatus.FAILURE,
                output_message="Not able to create payment session id"
        )
        
        response_json = api_response.json()
        payment_session_id = response_json.get("payment_session_id")
        self.create_payment_object_in_db(order_details_dict)

        return Output(
            output_details= {"payment_session_id": payment_session_id,},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully created the payment session id"
        )