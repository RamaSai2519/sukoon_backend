from models.common import Common
from models.interfaces import Output
from models.constants import OutputStatus
from db.referral import get_user_referral_collection


class Compute:
    def __init__(self) -> None:
        self.common = Common()
        self.referrals_collection = get_user_referral_collection()

    def get_distinct_users(self) -> list:
        return list(self.referrals_collection.distinct("userId"))

    def get_referrals(self, user_id: str) -> list:
        filter = {"userId": user_id}
        return list(self.referrals_collection.distinct("referredUserId", filter))

    def compute(self) -> Output:
        user_ids = self.get_distinct_users()
        users = []
        for user_id in user_ids:
            user_referrals = self.get_referrals(user_id)
            user = {
                "user": self.common.get_user_name(user_id),
                "referrals": [self.common.get_user_name(referral) for referral in user_referrals],
                "referral_count": len(user_referrals)
            }
            users.append(Common.jsonify(user))

        users.sort(key=lambda x: x["referral_count"], reverse=True)

        return Output(
            output_details=users,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched user(s)"
        )
