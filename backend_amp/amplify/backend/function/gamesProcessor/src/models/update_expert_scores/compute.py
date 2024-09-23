from models.constants import OutputStatus
from models.interfaces import UpdateScoresInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self) -> Output:
        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message="message"
        )
