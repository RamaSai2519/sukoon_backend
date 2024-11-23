from shared.models.interfaces import CreateNonRegisteredUserInput as Input, Output
from shared.models.constants import OutputStatus
from db_queries.mutations.user import create_non_registered_user


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self):

        user = create_non_registered_user(self.input.mobile_number)

        return Output(
            output_details="",
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully created non registered user"
        )
