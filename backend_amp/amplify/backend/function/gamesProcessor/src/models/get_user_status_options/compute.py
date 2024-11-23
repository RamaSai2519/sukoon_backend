from shared.models.constants import OutputStatus, user_status_options
from shared.models.interfaces import GetUserStatusesInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self) -> Output:

        return Output(
            output_details={'data': user_status_options},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched options"
        )
