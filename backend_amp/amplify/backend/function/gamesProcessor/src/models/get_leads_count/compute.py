from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.models.interfaces import GetLeadsCountInput as Input, Output
from shared.db.users import get_user_collection, get_meta_collection
from shared.db.calls import get_calls_collection
import time


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.calls_collection = get_calls_collection()
        self.users_collection = get_user_collection()
        self.today_query = Common.get_today_query("createdDate")

    def get_user_query(self, leads: bool) -> dict:
        query = {"profileCompleted": not leads}
        return query

    def get_counts(self, leads_query: dict, non_leads_query: dict) -> dict:
        collection = self.users_collection
        leads_count = collection.count_documents(leads_query)
        non_leads_count = collection.count_documents(non_leads_query)

        today_leads_count = collection.count_documents(
            {**leads_query, **self.today_query})
        today_non_leads_count = collection.count_documents(
            {**non_leads_query, **self.today_query})

        call_counts = self.calculate_call_counts()

        return {
            "total_leads": leads_count,
            "non_leads": non_leads_count,
            "today_leads": today_leads_count,
            "today_non_leads": today_non_leads_count,
            "one_call_users": call_counts["one_call_users"],
            "two_call_users": call_counts["two_call_users"],
            "repeat_users": call_counts["repeat_call_users"]
        }

    def calculate_call_counts(self) -> dict:
        pipeline = [
            {"$match": {"status": "successful"}},
            {"$group": {"_id": "$user", "call_count": {"$sum": 1}}},
            {"$project": {
                "_id": 1,
                "call_count": 1,
                "category": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$call_count", 1]},
                                "then": "one_call_users"},
                            {"case": {"$eq": ["$call_count", 2]},
                                "then": "two_call_users"},
                            {"case": {"$gt": ["$call_count", 2]},
                                "then": "repeat_call_users"}
                        ],
                        "default": None
                    }
                }
            }},
            {"$match": {"category": {"$ne": None}}},
            {"$group": {"_id": "$category", "user_count": {"$sum": 1}}}
        ]

        results = list(self.calls_collection.aggregate(pipeline))

        counts_dict = {"one_call_users": 0,
                       "two_call_users": 0, "repeat_call_users": 0}
        for result in results:
            counts_dict[result["_id"]] = result["user_count"]

        return counts_dict

    def compute(self) -> Output:
        leads_query = self.get_user_query(leads=True)
        non_leads_query = self.get_user_query(leads=False)

        counts = self.get_counts(leads_query, non_leads_query)

        return Output(output_details=counts)
