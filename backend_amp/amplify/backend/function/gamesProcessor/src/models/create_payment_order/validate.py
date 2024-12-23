from shared.models.interfaces import CreatePaymentOrderInput as Input
from shared.models.constants import pay_types


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        types = [pay_type["type"] for pay_type in pay_types]
        if self.input.pay_type and self.input.pay_type not in types:
            return False, "Invalid payment type"

        return True, ""
