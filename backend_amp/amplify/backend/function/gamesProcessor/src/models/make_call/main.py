import traceback
from models.constants import OutputStatus
from models.make_call.compute import Compute
from models.make_call.validate import Validator
from models.interfaces import CallInput as Input, Output


class MakeCall:
    def __init__(self, input: Input) -> None:
        self.input = input

    def process(self) -> Output:
        input = self.input
        valid_input, error_message = self._validate(input)

        if not valid_input:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"INVALID_INPUT: {error_message}"
            )
        
        try:
            output = self._compute(input)
        except Exception as e:
            print(traceback.format_exc(), "make_call/main.py")
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"ERROR: {str(e)}"
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