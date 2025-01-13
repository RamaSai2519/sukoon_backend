from shared.models.interfaces import GetPromptsInput as Input, Output
from shared.db.chat import get_prompt_proposals_collection
from shared.models.constants import OutputStatus
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.prompt_proposals_collection = get_prompt_proposals_collection()

    def compute(self) -> Output:
        prompts = self.prompt_proposals_collection.find()
        if not prompts:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="No prompts found"
            )

        prompts = list(prompts)

        return Output(
            output_details=Common.jsonify(prompts),
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched prompt(s)"
        )
