from shared.models.interfaces import UpdateFCMTokenInput as Input, Output
from shared.db.users import get_user_fcm_token_collection
from shared.models.constants import OutputStatus
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def _update_fcm_token(self, user_id, fcm_token) -> None:

        user_fcm_token_collection = get_user_fcm_token_collection()

        user_fcm_token_data = {
            "userId": user_id,
            "fcmToken": fcm_token,
            "createdAt": Common.get_current_utc_time(),
        }
        user_fcm_token_collection.insert_one(user_fcm_token_data)

    def compute(self):

        self._update_fcm_token(self.input.user_id, self.input.fcm_token)

        return Output(
            output_details="",
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully updated FCM token"
        )
