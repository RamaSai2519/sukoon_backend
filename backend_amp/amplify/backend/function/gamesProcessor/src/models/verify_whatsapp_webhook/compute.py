from shared.models.interfaces import GetWhatsappWebhookInput as Input


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self):

        verify_token = self.input.hub_verify_token
        if verify_token == "sukoon_verification":
            return self.input.hub_challenge

        return "Not able to verify webhook"
