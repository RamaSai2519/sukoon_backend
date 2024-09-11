from pprint import pprint
from models.common import Common
from models.interfaces import Output
from db.users import get_user_collection
from models.constants import OutputStatus
from db.referral import get_user_referral_collection
from pymongo.command_cursor import CommandCursor


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

    def compute(self) -> Output:
        user_referrals = self.get_user_referrals()
        community_referrals = self.get_community_referrals()
        referrals = {
            "userReferrals": [self.common.jsonify(ref) for ref in user_referrals],
            "communityReferrals": list(community_referrals)
        }

        return Output(
            output_details=referrals,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched user(s)"
        )
