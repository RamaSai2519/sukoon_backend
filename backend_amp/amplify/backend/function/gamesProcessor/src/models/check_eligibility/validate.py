from shared.models.interfaces import CheckEligiblilityInput as Input
from shared.models.constants import user_balance_types


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        if self.input.intent not in ['check', 'perform', 'done']:
            return False, "Invalid intent"

        if self.input.balance not in user_balance_types:
            return False, "Invalid balance field"

        return True, ""
