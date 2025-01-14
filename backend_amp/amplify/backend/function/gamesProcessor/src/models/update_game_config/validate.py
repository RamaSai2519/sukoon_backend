from shared.models.interfaces import UpdateGameConfigInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        game_config = self.input.game_config

        level = game_config.get("level")
        if not level or level <= 0:
            return False, "Level should be greater than 0"

        return True, ""
