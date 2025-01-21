from shared.models.common import Common
from shared.models.interfaces import StCallInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self) -> Output:

        return Output(
            output_details=Common.jsonify(self.input.__dict__)
        )
