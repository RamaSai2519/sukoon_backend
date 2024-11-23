import traceback
from shared.models.interfaces import UpdateGamePlayInput as Input, Output
from shared.models.constants import OutputStatus
from models.update_game_play.compute import Compute
from models.update_game_play.validate import Validator


class GetGamePlay:
    def __init__(self, input: Input) -> None:
        self.input = input

    def process(self):
        input = self.input
        valid_input, error_message = self._validate(input)

        if not valid_input:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"INVALID_INPUT. {error_message}",
            )

        try:
            output = self._compute(input)
        except Exception as e:
            print(traceback.format_exc())
            output = Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"{e}",
            )

        return output

    def _validate(self, input: Input):
        validation_obj = Validator(input)
        validation_result, error_message = validation_obj.validate_input()

        return validation_result, error_message

    def _compute(self, input: Input) -> Output:
        computation_obj = Compute(input)
        output = computation_obj.compute()

        return output
