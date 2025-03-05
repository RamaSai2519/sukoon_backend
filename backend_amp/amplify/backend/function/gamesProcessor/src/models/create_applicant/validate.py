from shared.models.interfaces import ApplicantInput as Input
from shared.models.constants import TimeFormats
from datetime import datetime


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.formType not in ["event", "sarathi", "ambassador"]:
            return False, "Invalid Form Type"

        if len(self.input.phoneNumber) != 10:
            return False, "Invalid Phone Number"

        if str(self.input.gender).lower() not in ["male", "female", "notSay"]:
            return False, "Invalid Gender"

        try:
            datetime.strptime(self.input.dateOfBirth,
                              TimeFormats.ANTD_TIME_FORMAT)
        except:
            return False, "Invalid Date of Birth"

        return True, ""
