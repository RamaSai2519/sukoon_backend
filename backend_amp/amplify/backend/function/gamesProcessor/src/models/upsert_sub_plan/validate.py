from shared.models.interfaces import UpsertSubPlanInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:

        if ' ' in self.input.name:
            return False, 'Name should not contain spaces'

        return True, ''
