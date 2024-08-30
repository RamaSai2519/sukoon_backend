from db.users import get_user_collection
from models.common import Common
from bson import ObjectId
from typing import Union
import re


class UsersHelper:
    def __init__(self):
        self.common = Common()
        self.users_collection = get_user_collection()

    def prep_projection(self, single_user: bool = False):
        projection = {"__v": 0, "lastModifiedBy": 0, "userGameStats": 0}
        if single_user:
            return projection
        projection["Customer Persona"] = 0
        return projection

    def __format__(self, user: dict, single_user: bool = False) -> dict:
        if single_user:
            # Get calls, events and referrals
            query = {"user": ObjectId(user["_id"])}
            user["calls"] = self.common.get_calls(query)

            query = {"userId": ObjectId(
                user["_id"]), "phoneNumber": user["phoneNumber"]}
            user["events"] = self.common.get_events_history(query)

            query = {"userId": user["_id"]}
            user["referrals"] = self.common.get_referrals(query)

        user["customerPersona"] = self.parse_user_persona(
            user.pop("Customer Persona", ""))
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

    def get_user(self, phoneNumber: str) -> Union[dict, None]:
        query = {"phoneNumber": phoneNumber}
        user = self.users_collection.find_one(
            query, self.prep_projection(True))
        if user:
            user = self.__format__(user, True)
            return user
        return None

    def get_users(self, size: int, page: int) -> list:
        if size and page:
            offset = int(int(page - 1) * size)
            users = list(self.users_collection.find(
                {}, self.prep_projection()).skip(offset).limit(int(size)).sort("name", 1))
        else:
            users = list(self.users_collection.find(
                {}, self.prep_projection()).sort("name", 1))
        users = [self.__format__(user) for user in users]
        return users
