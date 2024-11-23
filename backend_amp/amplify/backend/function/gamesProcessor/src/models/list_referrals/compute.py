from shared.models.common import Common
from shared.models.interfaces import Output
from shared.db.users import get_user_collection
from shared.models.constants import OutputStatus
from pymongo.command_cursor import CommandCursor
from shared.db.referral import get_user_referral_collection


class Compute:
    def __init__(self) -> None:
        self.common = Common()
        self.users_collection = get_user_collection()
        self.referrals_collection = get_user_referral_collection()

    def get_community_referrals(self) -> CommandCursor:
        user_referrals = self.users_collection.aggregate([
            {
                "$match": {
                    "refSource": {"$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$refSource",
                    "count": {"$sum": 1}
                }
            }
        ])

        return user_referrals

    def get_user_referrals(self) -> CommandCursor:
        community_referrals = self.referrals_collection.aggregate([
            {
                "$group": {
                    "_id": "$userId",
                    "count": {"$sum": 1}
                }
            }
        ])

        return community_referrals

    def __format__(self, format_spec: dict) -> dict:
        format_spec["user_name"] = self.common.get_user_name(
            format_spec["_id"])
        return self.common.jsonify(format_spec)

    def compute(self) -> Output:
        user_referrals = self.get_user_referrals()
        community_referrals = self.get_community_referrals()
        referrals = {
            "userReferrals": [self.__format__(ref) for ref in user_referrals],
            "communityReferrals": list(community_referrals)
        }

        return Output(
            output_details=referrals,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched referral(s)"
        )
