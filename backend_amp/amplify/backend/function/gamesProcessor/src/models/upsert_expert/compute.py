import pytz
import dataclasses
from typing import Union
from bson import ObjectId
from datetime import datetime
from shared.models.common import Common
from shared.models.constants import OutputStatus
from models.upsert_expert.slack import SlackManager
from shared.models.interfaces import Expert as Input, Output
from shared.db.experts import get_experts_collections, get_timings_collection, get_categories_collection, get_expertlogs_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.slack_manager = SlackManager()
        self.timings_collection = get_timings_collection()
        self.experts_collection = get_experts_collections()
        self.categories_collection = get_categories_collection()
        self.expertlogs_collection = get_expertlogs_collection()

    def set_defaults(self, expert_data: dict) -> dict:
        expert_data["active"] = True
        expert_data["isBusy"] = False
        expert_data["categories"] = []
        expert_data["highlights"] = []
        expert_data["type"] = "internal"
        expert_data["isDeleted"] = False
        expert_data["status"] = "offline"
        expert_data["profileCompleted"] = False
        expert_data["createdDate"] = datetime.now()
        return expert_data

    def merge_old_data(self, expert_data: dict, previous_data: dict) -> dict:
        for key, value in previous_data.items():
            if key not in expert_data or expert_data[key] is None or expert_data[key] == "" or expert_data[key] == []:
                expert_data[key] = value
        return expert_data

    def pop_immutable_fields(self, expert_data: dict) -> dict:
        fields = ["_id", "phoneNumber", "createdDate"]
        for field in fields:
            expert_data.pop(field, None)
        return expert_data

    def prep_data(self, expert_data: dict, previous_data: dict = None) -> dict:
        expert_data = {k: v for k, v in expert_data.items() if v is not None}
        if previous_data:
            expert_data = self.pop_immutable_fields(expert_data)
            expert_data = self.merge_old_data(expert_data, previous_data)
        else:
            expert_data = self.set_defaults(expert_data)

        if "sub_category" in expert_data:
            if isinstance(expert_data["sub_category"], list):
                expert_data["sub_category"] = [
                    ObjectId(item) if isinstance(item, str) else item
                    for item in expert_data["sub_category"]
                ]

        expert_data = self.populate_categories(expert_data)
        return expert_data

    def validate_phoneNumber(self, phoneNumber: str) -> Union[bool, dict]:
        expert = self.experts_collection.find_one({"phoneNumber": phoneNumber})
        return expert if expert else False

    def populate_categories(self, expert_data: dict):
        categories = expert_data.get("categories", [])
        categories = list(self.categories_collection.find(
            {"name": {"$in": categories}}))
        if not categories:
            return expert_data
        expert_data["categories"] = [
            str(category["_id"]) for category in categories]
        return expert_data

    def insert_blank_timings(self, expert_id) -> dict:
        days = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"]
        times = ["PrimaryStartTime", "PrimaryEndTime",
                 "SecondaryStartTime", "SecondaryEndTime"]

        for day in days:
            timing_docs = self.timings_collection.find(
                {"expert": ObjectId(expert_id)})
            if not any(timing_doc["day"] == day for timing_doc in timing_docs):
                self.timings_collection.insert_one(
                    {"expert": expert_id, "day": day, times[0]: "",
                     times[1]: "", times[2]: "", times[3]: ""})

    def handle_status(self, prev_expert: dict):
        status = self.input.status
        name = prev_expert.get("name")
        expert_id = str(prev_expert.get("_id"))
        number = prev_expert.get("phoneNumber")
        prev_status = prev_expert.get("status")

        if status is None:
            return "Status is unchanged"
        if status == prev_status:
            return f"Status is already {status}"

        current_time = datetime.now(pytz.utc)
        expert_obj_id = ObjectId(expert_id)

        if status == "online":
            self.expertlogs_collection.insert_one({
                "expert": expert_obj_id,
                status: current_time
            })
            return self.slack_manager.send_message(True, name, number)

        if status == "offline":
            online_time_object = dict(self.expertlogs_collection.find_one(
                {"expert": expert_obj_id, "offline": {"$exists": False}},
                sort=[("online", -1)]
            ))

            if not online_time_object:
                return "No online time found"

            onlinetime = online_time_object.get("online")
            onlinetime = datetime.strptime(
                str(onlinetime), "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=pytz.utc)
            duration = (current_time - onlinetime).total_seconds()

            self.expertlogs_collection.find_one_and_update(
                {"expert": expert_obj_id},
                {"$set": {status: current_time, "duration": int(duration)}},
                sort=[("online", -1)]
            )
            return self.slack_manager.send_message(False, name, number)

    def compute(self) -> Output:
        expert_data = self.input
        expert_data = dataclasses.asdict(expert_data)

        prev_expert = self.validate_phoneNumber(expert_data["phoneNumber"])

        if prev_expert:
            expert_data = self.prep_data(expert_data, prev_expert)
            self.experts_collection.update_one(
                {"phoneNumber": expert_data["phoneNumber"]},
                {"$set": expert_data}
            )
            response = self.handle_status(prev_expert)
            message = "Successfully updated expert and " + response
        else:
            expert_data = self.prep_data(expert_data)
            expert = self.experts_collection.insert_one(expert_data)
            self.insert_blank_timings(expert.inserted_id)
            message = "Successfully created expert"

        return Output(
            output_details=Common.jsonify(expert_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
