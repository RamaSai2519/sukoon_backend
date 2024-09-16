from models.interfaces import GetUsersInput as Input, Output
from models.constants import OutputStatus
from helpers.users import UsersHelper
from models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.helper = UsersHelper()

    def populate_schedules(self, user: dict) -> dict:
        query = {"user": ObjectId(user["_id"]),
                 "status": self.input.schedule_status}
        user[f"{self.input.schedule_status}_schedules"] = self.common.get_schedules(
            query)
        query = {"user": ObjectId(user["_id"])}
        user["schedule_counts"] = self.common.get_schedules_counts(query)
        return user

    def compute(self) -> Output:
        if self.input.phoneNumber is not None:
            users = self.helper.get_user(self.input.phoneNumber)
            if not users:
                return Output(
                    output_details={},
                    output_status=OutputStatus.FAILURE,
                    output_message="User not found"
                )
            if self.input.schedule_status is not None:
                users = self.populate_schedules(users)
        else:
            users = self.helper.get_users(self.input.size, self.input.page)

        return Output(
            output_details=users,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched user(s)"
        )
