from shared.models.interfaces import UpdateTimingsInput as Input
from shared.models.constants import expert_times


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.times = expert_times

    def validate_input(self):
        if self.input.row.field not in self.times:
            return False, "Invalid field"

        return True, None
