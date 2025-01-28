import traceback
from shared.models.constants import OutputStatus
from models.upsert_blogposts.compute import Compute
from models.upsert_blogposts.validate import UpsertValidator
from shared.models.interfaces import BlogPostInput as Input, Output

class UpsertBlogPost:
    def __init__(self, input: Input) -> None:
        self.input = input

    def process(self) -> Output:
        input = self.input

        valid_input, error_message = self._validate(input)
        if not valid_input:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"INVALID_INPUT. {error_message}",
            )

        try:
            output = self._upsert(input)
        except Exception as e:
            print(traceback.format_exc())
            output = Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"{e}",
            )

        return output

    def _validate(self, input: Input):
        validation_obj = UpsertValidator(input)
        validation_result, error_message = validation_obj.validate_input()
        return validation_result, error_message

    def _upsert(self, input: Input) -> Output:
        computation_obj = Compute(input)
        output = computation_obj.upsert_blogposts()
        return output
