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
        doc = {
            'action': self.input.balance,
            'user': ObjectId(self.input.user),
            'created_at': Common.get_current_utc_time()
        }
        inserted_id = self.tokens_collection.insert_one(doc).inserted_id
        doc['_id'] = inserted_id
        token = create_access_token(
            identity=str(inserted_id),
            expires_delta=timedelta(minutes=5)
        )
        doc['token'] = token

        return Output(
            output_message="Token generated",
            output_details=Common.jsonify(doc)
        )

    @jwt_required()
    def check_token(self) -> bool:
        try:
            doc_id = get_jwt_identity()
            query = {'_id': ObjectId(doc_id)}
            doc = self.tokens_collection.find_one(query)
            if not doc:
                return False

            if doc['user'] != ObjectId(self.input.user) or doc['action'] != self.input.balance:
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

        if self.check_token() == True:
            balance[self.input.balance] -= 1
            self.balances_collection.update_one(query, {"$set": balance})
            return Output(output_message="Token verified and balance updated")

        return Output(
            output_message="Token invalid",
            output_status=OutputStatus.FAILURE
        )
