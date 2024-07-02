from models.interfaces import ValidateOTPInput as Input, Output
from models.constants import OutputStatus
from db.otp import get_otp_collection


class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input
 

    def _validate_otp(self) -> dict:
        phone_number = self.input.phone_number
        otp = self.input.otp

        otp_collection = get_otp_collection()

        record = otp_collection.find_one({'phoneNumber': phone_number, 'otp': otp})
        
        if not record:
            return  "Invalid OTP", OutputStatus.FAILURE
        
        # OTP is valid
        otp_collection.delete_one({'_id': record['_id']})  # Optionally delete the OTP after validation
        
        return  "OTP validated successfully", OutputStatus.SUCCESS


    def compute(self):
        message, output_status = self._validate_otp()

        return Output(
            output_details= {},
            output_status=output_status,
            output_message=message
        )