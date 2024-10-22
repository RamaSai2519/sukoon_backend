from openai import AzureOpenAI
from configs import CONFIG as config


class GPT_Client:
    def __init__(self) -> None:
        self.key = config.GPT_API_KEY
        self.version = config.GPT_VERSION
        self.endpoint = config.GPT_ENDPOINT
        self.client = self._create_gpt_client()

    def _create_gpt_client(self) -> AzureOpenAI:
        return AzureOpenAI(
            api_key=self.key,
            api_version=self.version,
            azure_endpoint=self.endpoint
        )

    def get_gpt_client(self) -> AzureOpenAI:
        return self.client


class ADA_Client:
    def __init__(self) -> None:
        self.key = config.ADA_API_KEY
        self.version = config.ADA_VERSION
        self.endpoint = config.ADA_ENDPOINT
        self.client = self._create_ada_client()

    def _create_ada_client(self) -> AzureOpenAI:
        return AzureOpenAI(
            api_key=self.key,
            api_version=self.version,
            azure_endpoint=self.endpoint
        )

    def get_ada_client(self) -> AzureOpenAI:
        return self.client
