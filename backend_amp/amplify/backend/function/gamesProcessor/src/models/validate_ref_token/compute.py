from bson import ObjectId
from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.db.referral import get_ref_tokens_collection
from shared.db.referral import get_ref_tracks_collection
from shared.models.interfaces import ValidateRefTokenInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.ref_tokens_collection = get_ref_tokens_collection()
        self.ref_tracks_collection = get_ref_tracks_collection()

    def validate_token(self) -> bool:
        query = {'token': self.input.token}
        token_doc = self.ref_tokens_collection.find_one(query)
        return True if token_doc else False

    def get_user(self) -> dict:
        query = {'_id': ObjectId(self.input.user_id)}
        projection = {'name': 1, 'city': 1, 'birthDate': 1, 'phoneNumber': 1}
        user = self.ref_tracks_collection.find_one(query, projection)
        user['phoneNumber'] = user['phoneNumber'][-4:]
        user['phoneNumber'] = '******' + user['phoneNumber']
        return user

    def compute(self) -> Output:
        if not self.validate_token():
            return Output(output_status=OutputStatus.FAILURE, output_message='Invalid token')

        user = self.get_user()
        if not user:
            return Output(output_status=OutputStatus.FAILURE, output_message='User not found')

        return Output(
            output_status=OutputStatus.SUCCESS,
            output_message='Valid token',
            output_details=Common.jsonify(user)
        )
