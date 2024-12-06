from shared.models.interfaces import CreatePaymentOrderInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        pay_types = ["sarathiBal", "expertBal", "club", "code"]
        if self.input.pay_type not in pay_types:
            return False, "Invalid payment type"

        return True, ""
