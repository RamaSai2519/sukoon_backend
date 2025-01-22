# Compute File
from shared.models.interfaces import ValidateRefTokenInput as Input, Output
from shared.models.constants import OutputStatus
from shared.db.ref_tokens import get_ref_tokens_collection
from shared.db.ref_tracks import get_ref_tracks_collection
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.ref_tokens_collection = get_ref_tokens_collection()
        self.ref_tracks_collection = get_ref_tracks_collection()

    def compute(self) -> Output:
        token_doc = self.ref_tokens_collection.find_one(
            {"token": self.input.token})

        if not token_doc:
            return Output(
                output_details={"isToken": False},
                output_status=OutputStatus.FAILURE,
                output_message="Invalid referral token."
            )

        user_doc = self.ref_tracks_collection.find_one(
            {"user_id": self.input.user_id})

        if not user_doc:
            return Output(
                output_details={"isToken": True, "isUser": False},
                output_status=OutputStatus.FAILURE,
                output_message="User not found."
            )

        phone_number = user_doc.get("phoneNumber", "")
        masked_phone = f"******{phone_number[-4:]}" if phone_number else "Unavailable"

        user_details = {
            "name": user_doc.get("name", "Unknown"),
            "city": user_doc.get("city", "Unknown"),
            "birthDate": user_doc.get("birthDate", "Unknown"),
            "phoneNumber": masked_phone
        }

        return Output(
            output_details={"isToken": True,
                            "isUser": True, "user": user_details},
            output_status=OutputStatus.SUCCESS,
            output_message="Referral token and user validated successfully."
        )
