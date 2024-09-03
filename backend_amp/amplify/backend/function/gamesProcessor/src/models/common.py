from db.calls import get_calls_collection, get_schedules_collection
from models.constants import calls_exclusion_projection
from db.referral import get_user_referral_collection
from db.events import get_event_users_collection
from flask_jwt_extended import get_jwt_identity
from db.experts import get_experts_collections
from db.users import get_user_collection
from datetime import datetime, date
from bson import ObjectId


class Common:
    def __init__(self):
        self.referrals_collection = get_user_referral_collection()
        self.schedules_collection = get_schedules_collection()
        self.experts_collection = get_experts_collections()
        self.calls_collection = get_calls_collection()
        self.users_collection = get_user_collection()
        self.experts_cache = {}
        self.users_cache = {}

    @staticmethod
    def get_identity() -> str:
        return get_jwt_identity()

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

    @staticmethod
    def duration_str_to_seconds(duration: str) -> int:
        duration = duration.split(":")
        hours, minutes, seconds = map(int, duration)
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def seconds_to_duration_str(seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        formatted_duration = []
        if hours > 0:
            formatted_duration.append(f"{int(hours)}h")

        if minutes > 0:
            formatted_duration.append(f"{int(minutes)}m")

        if seconds > 0:
            formatted_duration.append(f"{int(seconds)}s")

        return " ".join(formatted_duration) if formatted_duration else "0s"

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
            call["user"] = self.get_user_name(user_id=ObjectId(
                call["user"])) if "user" in call else "Unknown"
            call["expert"] = self.get_expert_name(
                ObjectId(call["expert"])) if "expert" in call else "Unknown"
            call["conversationScore"] = call.pop("Conversation Score", 0)
            call = Common.jsonify(call)
            if "failedReason" in call and call["failedReason"] == "call missed":
                call["status"] = "missed"
            if "status" in call and call["status"] == "successfull":
                call["status"] = "successful"
        return calls

    def get_events_history(self, query: dict) -> list:
        events = list(get_event_users_collection().find(query))
        events = [Common.jsonify(event) for event in events]
        return events

    def get_referrals(self, query: dict) -> list:
        referrals = list(self.referrals_collection.find(query))
        referrals = [Common.jsonify(referral) for referral in referrals]
        return referrals

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

    def get_calls(self, query: dict = {}, projection: dict = {}, exclude: bool = True, format: bool = True) -> list:
        if exclude:
            projection = {**projection, **calls_exclusion_projection}

        calls = list(self.calls_collection.find(
            query, projection).sort("initiatedTime", -1))

        if format:
            calls = self.format_calls(calls)

        return calls
