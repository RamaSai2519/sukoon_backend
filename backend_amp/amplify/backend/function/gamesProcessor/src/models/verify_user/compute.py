from models.interfaces import VerifyUserInput as Input, Output
from db.users import get_prusers_collection
from models.constants import OutputStatus
from models.common import Common
from bson import ObjectId
import base64


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.prusers_collection = get_prusers_collection()

    def int_to_string(self, n: int) -> str:
        byte_length = (n.bit_length() + 7) // 8
        encoded_bytes = n.to_bytes(byte_length, 'big')
        decoded_string = base64.b64decode(encoded_bytes).decode('utf-8')
        return decoded_string

    def compute(self) -> Output:
        user_id = self.int_to_string(int(self.input.hash_code))
        user = self.prusers_collection.find_one({"_id": ObjectId(user_id)})
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
