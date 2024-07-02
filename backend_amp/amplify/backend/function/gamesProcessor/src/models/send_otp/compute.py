import string
import requests
from configs import CONFIG as Config
from models.interfaces import SendOTPInput as Input, Output
from models.constants import OutputStatus
from db.otp import get_otp_collection
import random

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input
 
    def _generate_otp(self, length=6):
        return ''.join(random.choices(string.digits, k=length))
    
    def _send_otp_via_sms(self, phone_number, otp):
        query_params = Config.SMS_API_CONFIG
        msg = query_params.get("msg")
        msg = msg.replace("__otp__", otp)
        query_params["msg"] = msg
        query_params["send_to"] = "91" + phone_number

        response = requests.get(url= Config.SMS_API_URL, params=query_params, verify=False)
        if response.text.startswith("success"):
            return "OTP generated and sent successfully", OutputStatus.SUCCESS
        return "Some error occured while sending OTP. Please try again", OutputStatus.FAILURE
        

    def _generate_and_send_otp(self):

        otp_collection = get_otp_collection()
        record = otp_collection.find_one({"phoneNumber": self.input.phone_number})
        if not record:

            otp = self._generate_otp()

            otp_collection.insert_one({
                'phoneNumber': self.input.phone_number,
                'otp': otp,
            })
        else:
            otp = record.get("otp")
        
        status_code, message = self._send_otp_via_sms(self.input.phone_number, otp)
        return status_code, message


    def compute(self):

        message, output_status = self._generate_and_send_otp()

        return Output(
            output_details= {},
            output_status=output_status,
            output_message=message
        )