from openai import AzureOpenAI
from configs import CONFIG as Config


class AzureOpenAIConfig:
    def __init__(self) -> None:
        self.azure_key = Config.AZURE_KEY
        self.azure_endpoint = Config.AZURE_ENDPOINT
        self.azure_version = Config.AZURE_API_VERSION
        self.openai_client = self._create_openai_client()

    def _create_openai_client(self) -> AzureOpenAI:
        return AzureOpenAI(
            api_key=self.azure_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.azure_version
        )

    def get_openai_client(self) -> AzureOpenAI:
        return self.openai_client
