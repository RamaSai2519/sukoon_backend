from shared.models.constants import OutputStatus, user_status_options, pay_types
from shared.models.interfaces import GetUserStatusesInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self) -> Output:
        if self.input.type == 'pay_types':
            options = pay_types
        else:
            options = user_status_options

        return Output(
            output_details={'data': options},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched options"
        )
