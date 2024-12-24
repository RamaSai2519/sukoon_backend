from shared.models.interfaces import UpsertPromptInput as Input, Output
from shared.db.chat import get_system_prompts_collection
from shared.models.constants import OutputStatus
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.system_prompts_collection = get_system_prompts_collection()

    def compute(self) -> Output:
        prompt = self.system_prompts_collection.find_one_and_update(
            filter={"context": self.input.context},
            update={"$set": {"content": self.input.content}},
            upsert=True,
            return_document=True
        )

        return Output(
            output_details=Common.jsonify(prompt),
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully upserted prompt"
        )
