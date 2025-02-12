from shared.models.interfaces import ChatInput as Input, Output
from shared.models.constants import OutputStatus
from shared.helpers.openai import GPT_Client
from shared.models.common import Common
from shared.schemas import BlogTags


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.message_history = []
        self.openai_client_obj = GPT_Client()
        self.openai_client = self.openai_client_obj.get_gpt_client()

    def get_response(self, message_history: list) -> str:
        if self.input.context == 'blog':
            response = self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-2024-11-20",
                messages=message_history,
                response_format=BlogTags
            )
            return response.choices[0].message.parsed.__dict__
        else:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=message_history,
            ).choices[0]
        print("Raw response from OpenAI:")
        print(response)
        return response.message.content

    def get_system_message(self) -> str:
        system_message = f"""
        You are a helpful AI assistant to help the user with their queries.
        You will provide relevant information to the user based on the context of the conversation.
        """
        return system_message

    def append_history(self, message: str, role: str) -> None:
        self.message_history.append({"role": role, "content": message})

    def compute(self) -> Output:
        self.append_history(self.get_system_message(), "system")
        self.append_history(self.input.prompt, "user")

        response = self.get_response(self.message_history)
        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched expert(s)"
        )
