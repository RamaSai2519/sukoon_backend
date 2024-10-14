from db.users import get_user_collection, get_user_notification_collection, get_user_webhook_messages_collection
from models.common import Common
from bson import ObjectId
from typing import Union
import re


class UsersHelper:
    def __init__(self):
        self.common = Common()
        self.users_collection = get_user_collection()
        self.notifications_collection = get_user_notification_collection()
        self.webhook_messages_collection = get_user_webhook_messages_collection()

    def prep_projection(self, single_user: bool = False) -> dict:
        projection = {"__v": 0, "lastModifiedBy": 0, "userGameStats": 0}
        if single_user:
            return projection
        projection["customerPersona"] = 0
        return projection

    def get_notifications(self, user_id_obj: ObjectId) -> list:
        query = {"userId": user_id_obj, "templateName": {"$exists": True}}
        notifications = list(self.notifications_collection.find(
            query).sort("createdAt", -1))
        return notifications

    def get_webhook_messages(self, user_id_obj: ObjectId) -> list:
        query = {"userId": user_id_obj, "body": {"$ne": None}}
        messages = list(self.webhook_messages_collection.find(
            query).sort("createdAt", -1))
        for message in messages:
            message["type"] = "Outgoing" if "templateName" in message else "Incoming"
        return messages

    def get_wa_history(self, user_id_obj: ObjectId) -> list:
        wa_history = self.get_notifications(user_id_obj)
        wa_history += self.get_webhook_messages(user_id_obj)
        wa_history = [Common.jsonify(history) for history in wa_history]
        return sorted(wa_history, key=lambda x: x["createdAt"], reverse=True)

    def __format__(self, user: dict, single_user: bool = False, internal: str = 'false', call_status: str = None) -> dict:
        if single_user:
            user_id_obj = ObjectId(user["_id"])
            exclude_query = self.common.get_internal_exclude_query(internal)
            query = {"user": user_id_obj, **exclude_query}
            if call_status:
                query["status"] = call_status
            user["calls"] = self.common.get_calls(query)

            query = {"userId": user_id_obj, "phoneNumber": user["phoneNumber"]}
            user["events"] = self.common.get_events_history(query)

            query = {"userId": user["_id"]}
            user["referrals"] = self.common.get_referrals(query)
            user["notifications"] = self.get_wa_history(user_id_obj)

        if "customerPersona" in user and isinstance(user["customerPersona"], str):
            user["customerPersona"] = self.parse_user_persona(
                user.get("customerPersona", ""))
        user["customerPersona"] = user.get("customerPersona", {})
        return Common.jsonify(user)

    def parse_user_persona(self, text: str) -> dict:
        result = {}
        sections = re.split(r'\n\s*####\s*[a-z]', text, flags=re.IGNORECASE)

        for section in sections:
            heading_pattern = r'^(?:\d+\.\s*)?\*\*(.*?):\*\*\s*(.*?)(?:\n\s*\*\*Confidence Score:\s*[\d.]+)?$'
            matches: list[str] = re.findall(
                heading_pattern, section, re.MULTILINE)

            for match in matches:
                heading = match[0].strip().lower().replace(
                    " ", "_").replace("/", "")
                content = match[1].replace("-", "").replace("**", "").strip()
                if heading and content:
                    result[heading] = {"value": content}

        return result

    def get_user(self, phoneNumber: str = None, user_id: str = None, internal: str = 'false', call_status: str = None) -> Union[dict, None]:
        if user_id:
            query = {"_id": ObjectId(user_id)}
        else:
            query = {"phoneNumber": phoneNumber}
        proj = self.prep_projection(True)
        user = self.users_collection.find_one(query, proj)
        if user:
            user = self.__format__(user, True, internal, call_status)
            return user
        return None

    def get_users(self, size: int = None, page: int = None, query: dict = {}) -> list:
        if size and page:
            offset = int(int(int(page) - 1) * int(size))
            users = list(self.users_collection.find(
                {}, self.prep_projection()).skip(offset).limit(int(size)).sort("name", 1))
        else:
            users = list(self.users_collection.find(
                query, self.prep_projection()).sort("name", 1))
        users = [self.__format__(user) for user in users]
        return users
