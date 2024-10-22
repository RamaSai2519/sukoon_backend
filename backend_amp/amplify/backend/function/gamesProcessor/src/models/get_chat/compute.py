from models.interfaces import ChatInput as Input, Output, Content
from models.constants import OutputStatus
from helpers.openai import GPT_Client
from models.common import Common
import json
import re


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.message_history = []
        self.openai_client_obj = GPT_Client()
        self.openai_client = self.openai_client_obj.get_gpt_client()

    def get_response(self, message_history: list) -> str:
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=message_history
        ).choices[0]
        # Print raw response for debugging
        print("Raw response from OpenAI:")
        print(response)
        return response.message.content

    def get_system_message(self) -> str:
        example_dict = json.dumps({
            "response": "Your response here",
            "category": "The category of the response here",
            "tags": ["tags", "related", "to", "the", "response"]
        })
        system_message = f"""
            You are a helpful AI assistant to help the user with their queries.
            You will provide relevant information to the user based on the context of the conversation.
            The response you will give should be in this format:
            {example_dict}
            """
        return system_message

    def __format__(self, format_spec: str) -> dict:
        if "json" in format_spec:
            response_text = re.search(
                r'```json\n(.*?)```', format_spec, re.DOTALL)
            if response_text:
                response_text = response_text.group(1)
                return response_text
        return format_spec

    def append_history(self, message: str, role: str) -> None:
        self.message_history.append({"role": role, "content": message})

    def manual_convert_to_dict(self, raw_string: str) -> dict:
        raw_string = raw_string.strip()

        result_dict = {}
        response_split = raw_string.split('"response": "', 1)
        category_split = response_split[1].split('", "category": "', 1)
        tags_split = category_split[1].split('", "tags": [', 1)

        response = category_split[0]
        category = tags_split[0]
        tags = tags_split[1].rstrip(']}').replace('"', '').split(', ')

        result_dict['response'] = response
        result_dict['category'] = category
        result_dict['tags'] = tags

        return result_dict

    def compute(self) -> Output:
        self.append_history(self.get_system_message(), "system")
        self.append_history(self.input.prompt, "user")

        response = self.get_response(self.message_history)
        response = self.__format__(response)
        response = self.manual_convert_to_dict(response)

        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched expert(s)"
        )
