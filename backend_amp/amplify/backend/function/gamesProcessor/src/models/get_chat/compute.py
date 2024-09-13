from models.interfaces import ChatInput as Input, Output
from helpers.openai import AzureOpenAIConfig
from models.constants import OutputStatus
from models.common import Common
import re


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.message_history = []
        self.openai_client_obj = AzureOpenAIConfig()
        self.openai_client = self.openai_client_obj.get_openai_client()

    def get_response(self, message_history: list) -> str:
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=message_history
        ).choices[0]
        print(response)
        return response.message.content

    def get_system_message(self) -> str:
        system_message = f"""
            You are an helpful AI assistant to help the user with their queries.
            You will provide relevant information to the user based on the context of the conversation.
            The reponse you will give should be in this format:
            {{"repsonse": "Your response here",
                "topic": "The topic of the response in one word"}}
            """
        return system_message

    def __format__(self, format_spec: str) -> str:
        response_text = re.search(
            r'```json\n(.*?)```', format_spec, re.DOTALL)
        return response_text.group(1) if response_text else ""

    def append_history(self, message: str, role: str):
        self.message_history.append({"role": role, "content": message})

    def compute(self) -> Output:
        self.append_history(self.get_system_message(), "system")
        self.append_history(self.input.prompt, "user")
        response = self.get_response(self.message_history)
        if "json" in response:
            response = self.__format__(response)

        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched expert(s)"
        )
