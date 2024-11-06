import json
from openai import AzureOpenAI
from models.constants import OutputStatus
from models.interfaces import ChatInput as Input, Output

class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.client = AzureOpenAI(
            api_version="2024-05-01-preview",
            azure_endpoint="https://techc-m1wpa2lt-australiaeast.openai.azure.com/",
            api_key='aeab9d95bfd540e5b9126b44048d1da0',
        )

    def get_pic(self) -> str:
        result = self.client.images.generate(
            model="dall-e-3", prompt=self.input.prompt, n=1)
        image_url = json.loads(result.model_dump_json())['data'][0]['url']

        return image_url

    def compute(self) -> Output:
        image_url = self.get_pic()

        return Output(
            output_details={"url": image_url},
            output_status=OutputStatus.SUCCESS,
            output_message="Image generated successfully",
        )