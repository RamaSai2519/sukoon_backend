from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from shared.models.interfaces import CheckEligiblilityInput as Input, Output
from shared.db.users import get_user_balances_collection
from shared.db.misc import get_tokens_collection
from shared.models.constants import OutputStatus
from shared.models.common import Common
from datetime import timedelta
from flask import request
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.tokens_collection = get_tokens_collection()
        self.balances_collection = get_user_balances_collection()

    def perform(self) -> Output:
        token = create_access_token(
            identity={
                'user': self.input.user,
                'action': self.input.balance
            },
            expires_delta=timedelta(minutes=5)
        )
        doc = {'token': token}
        self.tokens_collection.insert_one(doc)

        return Output(
            output_message="Token generated",
            output_details=Common.jsonify(doc)
        )

    @jwt_required()
    def check_token(self) -> bool:
        token = request.headers.get('Authorization').replace('Bearer ', '')
        query = {'token': token}
        if not self.tokens_collection.find_one(query):
            return False
        try:
            decoded = get_jwt_identity()
            if decoded['user'] != self.input.user or decoded['action'] != self.input.balance:
                return False
        except Exception:
            return False

        return True

    def compute(self) -> Output:
        query = {"user": ObjectId(self.input.user)}
        balance = self.balances_collection.find_one(query)
        if not balance:
            return Output(
                output_message="User not found",
                output_status=OutputStatus.FAILURE
            )
        req_balance = balance[self.input.balance]
        if req_balance <= 0:
            return Output(
                output_message="Insufficient balance",
                output_status=OutputStatus.FAILURE
            )

        if self.input.intent == "check":
            return Output(output_message="Eligible")

        if self.input.intent == "perform":
            return self.perform()

        # if self.check_token() == True:
        balance[self.input.balance] -= 1
        self.balances_collection.update_one(query, {"$set": balance})
        return Output(output_message="Token verified and balance updated")

        return Output(
            output_message="Token invalid",
            output_status=OutputStatus.FAILURE
        )
