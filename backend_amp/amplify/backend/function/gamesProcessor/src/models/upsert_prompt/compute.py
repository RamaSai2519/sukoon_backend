from shared.db.chat import get_system_prompts_collection, get_histories_collection, get_prompt_proposals_collection
from shared.models.interfaces import UpsertPromptInput as Input, Output
from shared.models.constants import OutputStatus
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.histories_collection = get_histories_collection()
        self.system_prompts_collection = get_system_prompts_collection()
        self.prompt_proposals_collection = get_prompt_proposals_collection()

    def compute(self) -> Output:
        if self.input.auth == 196970:
            query = {"context": self.input.context}
            content = self.input.content
            prompt = self.system_prompts_collection.find_one_and_update(
                filter={"context": self.input.context},
                update={"$set": {"content": content}},
                upsert=True,
                return_document=True
            )

            if self.input.context == 'ark_main':
                now_date = Common.get_current_utc_time()
                now_date = now_date.strftime('%Y-%m-%d')
                history_query = {'createdAt': now_date}
                update = {'$set': {'history.0.content': self.input.content}}
                self.histories_collection.update_many(
                    history_query, update)

            self.prompt_proposals_collection.update_one(
                query, {"$set": {"approved": True}})
            return Output(
                output_details=Common.jsonify(prompt),
                output_status=OutputStatus.SUCCESS,
                output_message="Successfully approved prompt"
            )

        prompt = self.prompt_proposals_collection.find_one_and_update(
            filter={"context": self.input.context},
            update={"$set": {"content": self.input.content, "approved": False}},
            upsert=True,
            return_document=True
        )

        return Output(
            output_details=Common.jsonify(prompt),
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully proposed prompt"
        )
