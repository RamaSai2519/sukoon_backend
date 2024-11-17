import traceback
from models.constants import OutputStatus
from models.invoice_generator.compute import Compute
from models.invoice_generator.validate import Validator
from models.interfaces import InvoiceData as Input, Output


class GenerateInvoice:
    def __init__(self, input: Input) -> None:
        self.input = input

    async def process(self) -> Output:
        input = self.input
        valid_input, error_message = self._validate(input)

        if not valid_input:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"INVALID_INPUT: {error_message}"
            )
        
        try:
            output = await self._compute(input)
        except Exception as e:
            print(traceback.format_exc())
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

    async def _compute(self, input: Input) -> Output:
        computation_obj = Compute(input)
        output = await computation_obj.compute()

        return output