from models.interfaces import ValidateOTPInput as Input, Output
from models.constants import OutputStatus
from helpers.experts import ExpertsHelper
from db.otp import get_otp_collection
from helpers.users import UsersHelper


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.user_helper = UsersHelper()
        self.expert_helper = ExpertsHelper()

    def _validate_otp(self) -> dict:
        phone_number = self.input.phone_number
        otp = self.input.otp

        otp_collection = get_otp_collection()
        query = {'phoneNumber': phone_number, 'otp': otp}
        record = otp_collection.find_one(query)
        if not record:
            return "Invalid OTP", OutputStatus.FAILURE

        otp_collection.delete_one({'_id': record['_id']})
        return "OTP validated successfully", OutputStatus.SUCCESS

    def populate_user_details(self) -> dict:
        if self.input.user_type == "user":
            return self.user_helper.get_user(self.input.phone_number, None, self.input.internal, self.input.call_status)
        return self.expert_helper.get_expert(self.input.phone_number)

    def compute(self) -> Output:
        message, output_status = self._validate_otp()
        if output_status == OutputStatus.SUCCESS:
            user_details = self.populate_user_details()
            return Output(
                output_details=user_details,
                output_status=output_status,
                output_message=message
            )

        return Output(
            output_details={},
            output_status=output_status,
            output_message=message
        )
