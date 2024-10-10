from models.interfaces import VerifyUserInput as Input, Output
from db.users import get_prusers_collection
from models.constants import OutputStatus
from models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.prusers_collection = get_prusers_collection()

    def compute(self) -> Output:
        user_id = self.common.get_identity()
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
