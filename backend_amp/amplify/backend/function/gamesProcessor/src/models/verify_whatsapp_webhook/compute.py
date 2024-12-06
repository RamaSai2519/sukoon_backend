from shared.models.interfaces import GetWhatsappWebhookInput as Input
from shared.configs import CONFIG as config


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self) -> str:

        if self.input.hub_mode and self.input.hub_verify_token == config.WHATSAPP_API['ACCESS_TOKEN']:
            if self.input.hub_mode == "subscribe":
                return self.input.hub_challenge

        return "Not able to verify webhook"
