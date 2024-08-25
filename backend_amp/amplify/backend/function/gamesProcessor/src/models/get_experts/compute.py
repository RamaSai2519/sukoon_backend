from db.experts import get_experts_collections, get_categories_collection, get_expertlogs_collection
from db.calls import get_calls_collection, get_schedules_collection
from models.interfaces import GetExpertsInput as Input, Output
from models.constants import OutputStatus
from models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.calls_collection = get_calls_collection()
        self.experts_collection = get_experts_collections()
        self.schedules_collection = get_schedules_collection()
        self.categories_collection = get_categories_collection()
        self.expertlogs_collection = get_expertlogs_collection()

    def prep_projection(self, req_cats: bool = False) -> dict:
        if req_cats:
            return {"__v": 0, "lastModifiedBy": 0}
        return {"__v": 0, "lastModifiedBy": 0, "categories": 0}

    def __format__(self, expert: dict, req_cats: bool = False) -> dict:
        if req_cats:
            expert = self.populate_categories(expert)
            expert["calls"] = self.get_calls_history(ObjectId(expert["_id"]))
        expert = self.populate_time_spent(expert)
        return Common.jsonify(expert)

    def format_calls(self, calls: list) -> list:
        for call in calls:
            call["user"] = self.common.get_user_name(
                user_id=ObjectId(call["user"]))
            call["expert"] = self.common.get_expert_name(
                ObjectId(call["expert"]))
            call = Common.jsonify(call)
        return calls

    def populate_categories(self, expert_data: dict) -> dict:
        cats = list(self.categories_collection.find(
            {"_id": {"$in": expert_data["categories"]}}))
        categories = []
        for cat in cats:
            categories.append(cat["name"])
        expert_data["categories"] = categories
        return expert_data

    def populate_time_spent(self, expert_data: dict) -> dict:
        query = {"expertId": expert_data["_id"], "duration": {"$exists": True}}
        total_time = list(
            self.expertlogs_collection.find(query, {"duration": 1}))
        total_time = sum(
            [
                log["duration"]
                for log in total_time
            ]
        )
        expert_data["timeSpent"] = round(
            (total_time / 3600), 2) if total_time else 0
        return expert_data

    def populate_schedules(self, expert: dict) -> dict:
        expert[f"{self.input.schedule_status}_schedules"] = self.get_schedules(
            expert["_id"])
        expert["schedule_counts"] = self.get_schedules_counts(
            expert["_id"])
        return expert

    def get_calls_history(self, expert_id: ObjectId) -> dict:
        query = {"expert": expert_id}
        calls = list(self.calls_collection.find(
            query).sort("initiatedTime", -1))
        calls = self.format_calls(calls)
        return calls

    def get_all_experts(self) -> list:
        experts = list(self.experts_collection.find(
            {}, self.prep_projection()).sort("name", 1))
        experts = [self.__format__(expert) for expert in experts]
        return experts

    def get_expert(self) -> dict:
        query = {"phoneNumber": self.input.phoneNumber}
        expert = dict(self.experts_collection.find_one(
            query, self.prep_projection(True)))
        if expert:
            experts = self.__format__(expert, True)
            return experts
        else:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="No expert found with the given phone number"
            )

    def get_schedules(self, expert_id: str) -> list:
        query = {"expert": ObjectId(
            expert_id), "status": self.input.schedule_status}
        schedules = list(self.schedules_collection.find(query))
        schedules = self.format_calls(schedules)
        return schedules

    def get_schedules_counts(self, expert_id: str) -> dict:
        statuses = ["pending", "completed", "missed"]
        counts = {}
        for status in statuses:
            query = {"expert": ObjectId(expert_id), "status": status}
            counts[status] = self.schedules_collection.count_documents(query)
        return counts

    def compute(self) -> Output:
        if self.input.phoneNumber is not None:
            experts = self.get_expert()
            if self.input.schedule_status is not None:
                experts = self.populate_schedules(experts)
        else:
            experts = self.get_all_experts()

        return Output(
            output_details=experts,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched expert(s)"
        )
