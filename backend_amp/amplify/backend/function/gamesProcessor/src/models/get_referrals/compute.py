from bson import ObjectId
from helpers.users import UsersHelper
from models.common import Common
from db.users import get_user_collection
from models.constants import OutputStatus
from db.referral import get_user_referral_collection
from models.interfaces import GetReferralsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.users_helper = UsersHelper()
        self.users_collection = get_user_collection()
        self.referrals_collection = get_user_referral_collection()

    def __format__(self, format_spec: dict, type: str = "com") -> dict:
        if type == "user":
            format_spec["referredUserName"] = self.common.get_user_name(
                format_spec["referredUserId"])
        return self.common.jsonify(format_spec)

    def get_user_referrals(self, user_id: str) -> list:
        referrals = list(self.referrals_collection.find(
            {"userId": ObjectId(user_id)}))
        return [self.__format__(referral, "user") for referral in referrals]

    def get_community_referrals(self, ref_code: str) -> list:
        return self.users_helper.get_users(query={"refSource": ref_code})

    def compute(self) -> Output:
        if self.input.userId:
            referrals = self.get_user_referrals(self.input.userId)
        else:
            referrals = self.get_community_referrals(self.input.refCode)

        return Output(
            output_details=referrals,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched referral(s)"
        )
