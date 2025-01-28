import traceback
from shared.models.constants import OutputStatus
from models.get_blogposts.compute import Compute
from models.get_blogposts.validate import Validate
from shared.models.interfaces import GetBlogPostsInput as Input, Output

class GetBlogPosts:
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
            output = self._compute(input)
        except Exception as e:
            print(traceback.format_exc())
            output = Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"An error occurred: {e}",
            )

        return output

    def _validate(self, input: Input) -> tuple:
        validation_obj = Validate(input)
        return validation_obj.validate_input()

    def _compute(self, input: Input) -> Output:
        computation_obj = Compute(input)
        return computation_obj.compute()
