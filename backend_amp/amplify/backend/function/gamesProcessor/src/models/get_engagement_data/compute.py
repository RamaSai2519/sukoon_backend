from bson import ObjectId
from typing import List, Dict
from datetime import datetime
from models.common import Common
from models.constants import OutputStatus
from db.calls import get_calls_collection
from models.constants import successful_calls_query
from db.users import get_user_collection, get_meta_collection
from models.interfaces import GetEngagementDataInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.page = int(input.page)
        self.size = int(input.size)
        self.current_time = datetime.now()
        self.calls_collection = get_calls_collection()
        self.meta_collection = get_meta_collection()
        self.users_collection = get_user_collection()
        self.meta_fields = ["remarks", "expert", "lastReached",
                            "status", "userStatus", "source"]

    def populate_meta_data(self, user: dict, query: dict) -> dict:
        meta_data: dict = self.meta_collection.find_one(query)
        for field in self.meta_fields:
            user[field] = meta_data.get(field, "") if meta_data else ""

        return user

    def populate_call_data(self, user: dict, query: dict) -> dict:
        query = {**query, **successful_calls_query}
        projection = {"_id": 0, "initiatedTime": 1, "expert": 1}
        sort = [("initiatedTime", -1)]
        last_call: dict = self.calls_collection.find_one(
            query, projection, sort=sort)

        if last_call:
            last_call_time = Common.string_to_date(last_call, "initiatedTime")
            user["lastCallDate"] = last_call_time
            user["callAge"] = (self.current_time - last_call_time).days
            user["expert"] = last_call.get("expert", "")
            user["expert"] = self.common.get_expert_name(user["expert"])
        else:
            user["lastCallDate"] = "No Calls"
            user["callAge"] = 0

        user["callsDone"] = self.calls_collection.count_documents(query)
        user["callStatus"] = self.common.get_call_status(user["callsDone"])

        return user

    def format_users(self, users: List[Dict]) -> list:
        for user in users:
            created_date = Common.string_to_date(user, "createdDate")
            user["slDays"] = (self.current_time - created_date).days
            user_profile = user.get("profileCompleted", False)
            user["type"] = "Lead" if user_profile is False else "User"
            population_query = {"user": user.get("_id")}

            user = self.populate_meta_data(user, population_query)
            user = self.populate_call_data(user, population_query)

            user = Common.jsonify(user)
        return users

    def get_users(self) -> list:
        projection = {"Customer Persona": 0}
        cursor = self.users_collection.find(
            {}, projection).sort("createdDate", 1)
        users = Common.paginate_cursor(cursor, self.page, self.size)
        users = self.format_users(list(users))
        return users

    def compute(self) -> Output:
        users = self.get_users()
        total = self.users_collection.count_documents({})

        final_doc = {"data": users, "total": total,
                     "page": self.page, "size": self.size}

        return Output(
            output_details=final_doc,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched data"
        )
