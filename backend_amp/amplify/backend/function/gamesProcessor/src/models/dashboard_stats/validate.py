from shared.models.interfaces import DashboardStatsInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.item not in ["stats", "insights"]:
            return False, "Invalid item"

        return True, ""
