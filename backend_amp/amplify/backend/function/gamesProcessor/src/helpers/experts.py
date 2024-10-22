from db.experts import get_experts_collections, get_categories_collection, get_expertlogs_collection
from models.common import Common
from bson import ObjectId


class ExpertsHelper:
    def __init__(self) -> None:
        self.common = Common()
        self.experts_collection = get_experts_collections()
        self.categories_collection = get_categories_collection()
        self.expertlogs_collection = get_expertlogs_collection()

    def prep_projection(self, req_cats: bool = False) -> dict:
        if req_cats:
            return {"__v": 0, "lastModifiedBy": 0}
        return {"__v": 0, "lastModifiedBy": 0, "categories": 0}

    def __format__(self, expert: dict, req_cats: bool = False) -> dict:
        if req_cats:
            expert = self.populate_categories(expert)
            query = {"expert": ObjectId(expert["_id"])}
            expert["calls"] = self.common.get_calls(query)
        expert = self.populate_time_spent(expert)
        expert = self.populate_days_logged_in(expert)

        return Common.jsonify(expert)

    def get_experts(self, query: dict = {}) -> list:
        experts = list(self.experts_collection.find(
            query, self.prep_projection()).sort("name", 1))
        experts = [self.__format__(expert) for expert in experts]
        return experts

    def get_expert(self, phoneNumber: str = None, expert_id: str = None) -> dict:
        query = {}
        if phoneNumber:
            query["phoneNumber"] = phoneNumber
        elif expert_id:
            query["_id"] = ObjectId(expert_id)
        else:
            return None
        expert = self.experts_collection.find_one(
            query, self.prep_projection(True))
        if expert:
            experts = self.__format__(dict(expert), True)
            return experts
        return None

    def populate_categories(self, expert_data: dict) -> dict:
        expert_categories = expert_data.get("categories")
        expert_categories = [
            ObjectId(cat) for cat in expert_categories] if expert_categories else []
        query = {"_id": {"$in": expert_categories}}
        cats = list(self.categories_collection.find(query))
        categories = []
        for cat in cats:
            categories.append(cat["name"])
        expert_data["categories"] = categories
        return expert_data

    def populate_time_spent(self, expert_data: dict) -> dict:
        query = {"expert": expert_data["_id"], "duration": {"$exists": True}}
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

    def populate_days_logged_in(self, expert_data: dict) -> dict:
        query = {"expert": expert_data["_id"]}
        times_logged_in = self.expertlogs_collection.distinct("online", query)

        days_logged_in = set([log.date() for log in times_logged_in])
        expert_data["daysLoggedIn"] = len(days_logged_in)

        return expert_data
