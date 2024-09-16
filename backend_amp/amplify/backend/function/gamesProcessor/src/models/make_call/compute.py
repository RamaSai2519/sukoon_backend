import requests
from bson import ObjectId
from datetime import datetime
from models.constants import OutputStatus
from db.users import get_user_collection
from db.calls import get_calls_collection
from db.experts import get_experts_collections
from models.interfaces import CallInput as Input, Output

class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()
        self.calls_collection = get_calls_collection()

    def compute(self) -> Output:
        user_id = self.input.user_id
        expert_id = self.input.expert_id

        user_number, expert_number = self.get_phone_numbers(user_id, expert_id)

        call_id = self._make_call(user_number, expert_number)
        if not call_id:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="Failed to make call"
            )
        
        db_update = self._update_db(user_id, expert_id, call_id)
        if not db_update:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="Failed to update DB"
            )
        
        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message=f"Call initiated with callid: {call_id}"
        )

    def get_phone_numbers(self, user_id: str, expert_id: str):
        user = self.users_collection.find_one({"_id": ObjectId(user_id)})
        expert = self.experts_collection.find_one({"_id": ObjectId(expert_id)})

        return user["phoneNumber"], expert["phoneNumber"]

    def _make_call(self, user_number: str, expert_number: str):
        knowlarity_url = "https://kpi.knowlarity.com/Basic/v1/account/call/makecall"
        headers = {
            "x-api-key": "bb2S4y2cTvaBVswheid7W557PUzUVMnLaPnvyCxI",
            "authorization": "0738be9e-1fe5-4a8b-8923-0fe503e87deb"
        }
        payload = {
            "k_number": "+918035384523",
            "agent_number": "+91" + expert_number,
            "customer_number": "+91" + user_number,
            "caller_id": "+918035384523"
        }
        response = requests.post(knowlarity_url, headers=headers, json=payload)
        if response.status_code != 200:
            print("Failed to make call")
            return False
        
        return response.json()["success"]["call_id"]
        
    def _update_db(self, user_id: str, expert_id: str, call_id: str) -> bool:
        user_update = self.users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"isBusy": True}})
        if user_update.modified_count == 0:
            print("Failed to update user")
            return False
        
        expert_update = self.experts_collection.update_one({"_id": ObjectId(expert_id)}, {"$set": {"isBusy": True}})
        if expert_update.modified_count == 0:
            print("Failed to update expert")
            return False
        
        call_insert = self.calls_collection.insert_one({"user": user_id, "expert": expert_id, "callId": call_id, "initiatedTime": datetime.now()})
        if call_insert.inserted_id is None:
            print("Failed to insert call")
            return False
        
        return True
        
