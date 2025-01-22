from bson import ObjectId
from shared.models.common import Common
from shared.db.users import get_user_collection
from shared.models.constants import OutputStatus
from shared.models.interfaces import ValidateRefTokenInput as Input, Output
from shared.db.referral import get_ref_tokens_collection, get_ref_tracks_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.ref_tokens_collection = get_ref_tokens_collection()
        self.ref_tracks_collection = get_ref_tracks_collection()

    def validate_token(self) -> bool:
        query = {'token': self.input.token}
        token_doc = self.ref_tokens_collection.find_one(query)
        return True if token_doc else False

    def get_user(self) -> dict:
        query = {'_id': ObjectId(self.input.user_id)}
        projection = {'name': 1, 'city': 1, 'birthDate': 1, 'phoneNumber': 1}
        user = self.users_collection.find_one(query, projection)
        user['phoneNumber'] = user['phoneNumber'][-4:]
        user['phoneNumber'] = '******' + user['phoneNumber']
        return user

    def track_referral(self) -> ObjectId:
        doc = {
            'user': ObjectId(self.input.user_id),
            'token': self.input.token,
            'device_id': self.input.device_id,
            'createdAt': Common.get_current_utc_time()
        }
        inserted_id = self.ref_tracks_collection.insert_one(doc).inserted_id
        return inserted_id

    def compute(self) -> Output:
        output_dict = {
            'isValidToken': False,
            'isValidUser': False,
            'user': None
        }
        if not self.validate_token():
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message='Invalid token',
                output_details=output_dict
            )
        output_dict['isValidToken'] = True

        user = self.get_user()
        if not user:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message='User not found',
                output_details=output_dict
            )
        output_dict['isValidUser'] = True
        output_dict['user'] = user

        self.track_referral()
        return Output(
            output_status=OutputStatus.SUCCESS,
            output_message='Valid token',
            output_details=Common.jsonify(output_dict)
        )
