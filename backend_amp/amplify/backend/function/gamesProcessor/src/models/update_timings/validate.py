from models.interfaces import UpdateTimingsInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.times = ["PrimaryStartTime", "PrimaryEndTime",
                      "SecondaryStartTime", "SecondaryEndTime"]
                    

    def validate_input(self):
        if self.input.row.field not in self.times:
            return False, "Invalid field"   
        

        return True, None
