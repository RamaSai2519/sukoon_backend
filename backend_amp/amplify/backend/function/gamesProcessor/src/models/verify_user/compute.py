from models.interfaces import VerifyUserInput as Input, Output
from db.users import get_prusers_collection
from models.constants import OutputStatus
from models.common import Common
from bson import ObjectId
import base64


class BarcodeDecoder:
    def __init__(self, barcode_result: str) -> None:
        self.barcode_result = barcode_result

    def decode_barcode_to_user_id(self) -> str:
        '''Decode the scanned barcode result to get the original user_id.'''
        # Decode the base64 string back to bytes
        # Adding '==' in case padding is missing
        decoded_bytes = base64.urlsafe_b64decode(self.barcode_result + '==')

        # Convert bytes back to the original string
        user_id = decoded_bytes.decode('utf-8')

        return user_id


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.prusers_collection = get_prusers_collection()

    def compute(self) -> Output:
        # barcode_decoder = BarcodeDecoder(self.input.hash_code)
        # user_id = barcode_decoder.decode_barcode_to_user_id()
        user = self.prusers_collection.find_one({"_id": ObjectId(self.input.hash_code)})
        if not user:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="User not found"
            )

        return Output(
            output_details=Common.jsonify(user),
            output_status=OutputStatus.SUCCESS,
            output_message="User found"
        )
