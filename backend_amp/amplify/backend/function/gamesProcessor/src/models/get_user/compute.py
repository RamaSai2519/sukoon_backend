from db.calls import get_calls_collection, get_schedules_collection
from models.interfaces import GetUsersInput as Input, Output
from models.constants import OutputStatus
from db.users import get_user_collection
from models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()
        self.schedules_collection = get_schedules_collection()

    def prep_projection(self, single_user: bool = False):
        projection = {"__v": 0, "lastModifiedBy": 0, "userGameStats": 0}
        if single_user:
            return projection
        projection["Customer Persona"] = 0
        return projection

    def __format__(self, user: dict, single_user: bool = False) -> dict:
        if single_user:
            query = {"user": ObjectId(user["_id"])}
            user["calls"] = self.common.get_calls_history(query)
        return Common.jsonify(user)

    def populate_schedules(self, user: dict) -> dict:
        query = {"user": ObjectId(user["_id"]),
                 "status": self.input.schedule_status}
        user[f"{self.input.schedule_status}_schedules"] = self.common.get_schedules(
            query)
        query = {"user": ObjectId(user["_id"])}
        user["schedule_counts"] = self.common.get_schedules_counts(query)
        return user

    def get_user(self):
        query = {"phoneNumber": self.input.phoneNumber}
        user = self.users_collection.find_one(
            query, self.prep_projection(True))
        if user:
            user = self.__format__(user, True)
            return user
        return None

    def get_all_users(self) -> list:
        if self.input.size and self.input.page:
            offset = int((int(self.input.page) - 1) * int(self.input.size))
            users = list(self.users_collection.find(
                {}, self.prep_projection()).skip(offset).limit(int(self.input.size)).sort("name", 1))
        else:
            users = list(self.users_collection.find(
                {}, self.prep_projection()).sort("name", 1))
        users = [self.__format__(user) for user in users]
        return users

    def compute(self) -> Output:
        if self.input.phoneNumber is not None:
            users = self.get_user()
            if not users:
                return Output(
                    output_details={},
                    output_status=OutputStatus.FAILURE,
                    output_message="User not found"
                )
            if self.input.schedule_status is not None:
                users = self.populate_schedules(users)
        else:
            users = self.get_all_users()

        return Output(
            output_details=users,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched user(s)"
        )
