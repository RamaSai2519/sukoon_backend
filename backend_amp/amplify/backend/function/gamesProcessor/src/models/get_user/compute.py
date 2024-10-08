from models.interfaces import GetUsersInput as Input, Output
from models.constants import OutputStatus
from helpers.users import UsersHelper
from models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.helper = UsersHelper()

    def compute(self) -> Output:
        if self.input.phoneNumber is not None:
            users = self.helper.get_user(self.input.phoneNumber)
            if not users:
                return Output(
                    output_details={},
                    output_status=OutputStatus.FAILURE,
                    output_message="User not found"
                )
        else:
            users = self.helper.get_users(self.input.size, self.input.page)

        return Output(
            output_details=users,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched user(s)"
        )
