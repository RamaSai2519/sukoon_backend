import dataclasses
from typing import Union
from bson import ObjectId
from datetime import datetime
from models.common import Common
from models.constants import OutputStatus
from models.interfaces import Expert as Input, Output
from db.experts import get_experts_collections, get_timings_collection, get_categories_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.timings_collection = get_timings_collection()
        self.experts_collection = get_experts_collections()
        self.categories_collection = get_categories_collection()

    def prep_data(self, expert_data: dict, new_expert=True):
        if new_expert:
            expert_data["active"] = False
            expert_data["isBusy"] = False
            expert_data["type"] = "saarthi"
            expert_data["status"] = "offline"
            expert_data["profileCompleted"] = True
            expert_data["createdDate"] = datetime.now()
        expert_data = self.populate_categories(expert_data)
        expert_data.pop("_id", None)
        expert_data = {k: v for k, v in expert_data.items() if v is not None}
        return expert_data

    def validate_phoneNumber(self, phoneNumber: str) -> Union[bool, dict]:
        expert = self.experts_collection.find_one({"phoneNumber": phoneNumber})
        return expert if expert else False

    def populate_categories(self, expert_data: dict):
        categories = expert_data.get("categories")
        if not categories:
            return expert_data
        categories = list(self.categories_collection.find(
            {"name": {"$in": categories}}))
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

    def compute(self) -> Output:
        expert_data = self.input
        expert_data = dataclasses.asdict(expert_data)

        if self.validate_phoneNumber(expert_data["phoneNumber"]):
            expert_data = self.prep_data(expert_data, new_expert=False)
            self.experts_collection.update_one(
                {"phoneNumber": expert_data["phoneNumber"]},
                {"$set": expert_data}
            )
            message = "Successfully updated expert"
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
