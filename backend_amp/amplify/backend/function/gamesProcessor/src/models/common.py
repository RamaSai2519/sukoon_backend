from db.calls import get_calls_collection, get_schedules_collection
from db.events import get_event_users_collection
from db.experts import get_experts_collections
from db.users import get_user_collection
from datetime import datetime, date
from bson import ObjectId


class Common:
    def __init__(self):
        self.schedules_collection = get_schedules_collection()
        self.experts_collection = get_experts_collections()
        self.calls_collection = get_calls_collection()
        self.users_collection = get_user_collection()
        self.experts_cache = {}
        self.users_cache = {}

    @staticmethod
    def jsonify(doc: dict) -> dict:
        for field, value in doc.items():
            if isinstance(value, ObjectId):
                doc[field] = str(value)
            elif isinstance(value, datetime):
                doc[field] = datetime.strftime(value, "%Y-%m-%dT%H:%M:%S")
        return doc

    @staticmethod
    def string_to_date(doc: dict, field: str) -> date:
        if field in doc:
            doc[field] = datetime.strptime(doc[field], "%Y-%m-%dT%H:%M:%S.%fZ")
        return doc[field]

    def get_user_name(self, user_id: ObjectId) -> str:
        users_cache = self.users_cache
        if user_id not in users_cache:
            user = self.users_collection.find_one(
                {"_id": user_id}, {"name": 1})
            users_cache[user_id] = (
                user["name"] if user and "name" in user else "Unknown"
            )
        return users_cache[user_id]

    def get_expert_name(self, expert_id: ObjectId) -> str:
        experts_cache = self.experts_cache
        if expert_id not in experts_cache:
            expert = self.experts_collection.find_one(
                {"_id": expert_id}, {"name": 1})
            experts_cache[expert_id] = (
                expert["name"] if expert and "name" in expert else "Unknown"
            )
        return experts_cache[expert_id]

    def format_calls(self, calls: list) -> list:
        for call in calls:
            call["user"] = self.get_user_name(
                user_id=ObjectId(call["user"]))
            call["expert"] = self.get_expert_name(
                ObjectId(call["expert"]))
            call["conversationScore"] = call.pop("Conversation Score", 0)
            call = Common.jsonify(call)
        return calls

    def get_calls_history(self, query: dict) -> list:
        calls = list(self.calls_collection.find(
            query).sort("initiatedTime", -1))
        calls = self.format_calls(calls)
        return calls

    def get_events_history(self, query: dict) -> list:
        events = list(get_event_users_collection().find(query))
        events = [Common.jsonify(event) for event in events]
        return events

    def get_schedules(self, query: dict) -> list:
        schedules = list(self.schedules_collection.find(query))
        schedules = self.format_calls(schedules)
        return schedules

    def get_schedules_counts(self, query: dict) -> dict:
        statuses = ["pending", "completed", "missed"]
        counts = {}
        for status in statuses:
            query["status"] = status
            counts[status] = self.schedules_collection.count_documents(query)
        return counts
