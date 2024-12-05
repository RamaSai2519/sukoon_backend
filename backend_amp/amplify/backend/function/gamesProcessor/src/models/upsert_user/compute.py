import json
import string
import random
import hashlib
import requests
import dataclasses
from bson import ObjectId
from datetime import datetime
from typing import Union, Tuple
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.db.users import get_user_collection
from models.upsert_user.slack import SlackManager
from shared.models.interfaces import User as Input, Output
from shared.db.referral import get_user_referral_collection
from shared.models.constants import OutputStatus, application_json_header


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.query = self.decide_query()
        self.slack_manager = SlackManager()
        self.users_collection = get_user_collection()
        self.referrals_collection = get_user_referral_collection()

    def decide_query(self) -> dict:
        query = {}
        if self.input.phoneNumber:
            query['phoneNumber'] = self.input.phoneNumber
        elif self.input._id:
            query['_id'] = ObjectId(self.input._id)
        return query

    def defaults(self, user_data: dict) -> dict:
        user_data['active'] = True
        user_data['isBusy'] = False
        user_data['isBlocked'] = False
        user_data['isPaidUser'] = False
        user_data['wa_opt_out'] = False
        user_data['numberOfGames'] = 0
        user_data['numberOfCalls'] = 3
        user_data.pop('_id', None)
        return user_data

    def pop_immutable_fields(self, user_data: dict) -> dict:
        fields = ['phoneNumber', 'refCode', 'createdDate']
        for field in fields:
            user_data.pop(field, None)
        return user_data

    def prep_data(self, user_data: dict, prev_user: dict = None) -> dict:
        if prev_user:
            user_data = self.pop_immutable_fields(user_data)
            user_data = Common.merge_dicts(user_data, prev_user)
        else:
            user_data = self.defaults(user_data)
        user_data.pop('refCode', None)

        user_data['profileCompleted'] = bool(
            user_data.get('name') and user_data.get('birthDate'))

        if user_data.get('profileCompleted') and (not prev_user or not prev_user.get('refCode')):
            user_data['refCode'] = self.generate_referral_code(
                user_data['name'], user_data['phoneNumber'])

        date_fields = ['createdDate', 'birthDate']
        for field in date_fields:
            if user_data.get(field) and not isinstance(user_data[field], datetime):
                user_data[field] = Common.string_to_date(user_data, field)

        object_fields = ['_id', 'expert']
        for field in object_fields:
            if user_data.get(field) and not isinstance(user_data[field], ObjectId):
                user_data[field] = ObjectId(user_data[field])

        user_data = Common.filter_none_values(user_data)
        return user_data

    def send_wa_message(self, payload: dict) -> None:
        url = config.URL + '/actions/send_whatsapp'
        headers = application_json_header
        response = requests.request(
            'POST', url, headers=headers, data=json.dumps(payload)
        )
        if response.status_code != 200:
            print(response.text)
        print(response.text)
        return True if response.status_code == 200 else False

    def generate_referral_code(self, name: str, phone_number: str) -> str:
        salt = ''.join(random.choices(string.ascii_letters, k=6))
        raw_data = name + phone_number + salt
        hash_object = hashlib.sha256(raw_data.encode())
        code = hash_object.hexdigest()[:8].upper()
        valid_code = self.validate_referral_code(code)
        return code if not valid_code else self.generate_referral_code(name, phone_number)

    def validate_referral_code(self, referral_code: str) -> Union[bool, dict]:
        user = self.users_collection.find_one({'refCode': referral_code})
        return user if user else False

    def validate_phoneNumber(self) -> Union[dict, None]:
        user = self.users_collection.find_one(self.query)
        return user if user else None

    def validate_referral(self, referred_user_id: str) -> bool:
        filter = {'referredUserId': referred_user_id}
        referral = self.referrals_collection.find_one(filter)
        return True if referral else False

    def insert_referral(self, referred_user_id: str, user_id: str) -> None:
        referral = {'referredUserId': referred_user_id, 'userId': user_id}
        if not self.validate_referral(referred_user_id):
            referral['createdAt'] = datetime.now()
            self.referrals_collection.insert_one(referral)

    def update_user(self, user_data: dict, prev_user: dict) -> str:
        self.users_collection.update_one(self.query, {'$set': user_data})

        if user_data.get('isPaidUser') == True and prev_user and prev_user.get('isPaidUser') == False:
            payload = {
                'phone_number': prev_user.get('phoneNumber', ''),
                'template_name': 'CLUB_SUKOON_MEMBERSHIP',
                'parameters': {
                    'user_name': str(str(prev_user.get('name', '')).split(' ')[0].capitalize())
                }
            }
            self.send_wa_message(payload)

        if user_data.get('profileCompleted') == True and prev_user and prev_user.get('profileCompleted') == False:
            user_number = user_data.get('phoneNumber')
            user_name = user_data.get('name', user_number)
            message = self.slack_manager.send_message(
                user_name, 'User', str(prev_user['_id']))
            response = self.send_insert_message(user_name, user_number, True)
            message += ' and sent welcome message' if response else ' but failed to send welcome message'

            return f'Successfully updated user{message}'

        return 'Successfully updated user'

    def insert_user(self, user_data: dict) -> Tuple[str, dict]:
        user_data['_id'] = self.users_collection.insert_one(
            user_data).inserted_id

        message = 'Successfully created user'
        user_number = user_data.get('phoneNumber')
        user_name = user_data.get('name', user_number)
        user_profile = user_data.get('profileCompleted', False)
        response = self.send_insert_message(
            user_name, user_number, user_profile)
        message += ' and sent welcome message' if response else ' but did not send welcome message'

        signup_type = 'User' if user_profile else 'Lead'
        message += self.slack_manager.send_message(
            user_name, signup_type, str(user_data['_id']))
        return message, user_data

    def handle_referral(self, user_data: dict, prev_user: dict) -> str:
        if self.input.refCode:
            referrer = self.validate_referral_code(self.input.refCode)
            if referrer and not user_data.get('refSource'):
                self.insert_referral(user_data['_id'], referrer['_id'])
            else:
                if not self.validate_referral(user_data['_id']) and (not prev_user or not prev_user.get('refSource')):
                    user_data['refSource'] = self.input.refCode
        self.users_collection.update_one(self.query, {'$set': user_data})

    def send_insert_message(self, name: str, phone_number: str, profileCompleted: bool):
        if profileCompleted == True:
            payload = {
                'template_name': 'PROMO_TEMPLATE',
                'phone_number': phone_number,
                'request_meta': json.dumps({'user_name': name}),
                'parameters': {'image_link': 'https://sukoon-media.s3.ap-south-1.amazonaws.com/wa_promo_image.jpeg'}
            }
            response = self.send_wa_message(payload)
            return response
        return None

    def compute(self) -> Output:
        user = self.input
        user_data = dataclasses.asdict(user)
        prev_user = self.validate_phoneNumber()

        user_data = self.prep_data(user_data, prev_user)
        if prev_user:
            message = self.update_user(user_data, prev_user)
        else:
            message, user_data = self.insert_user(user_data)
        self.handle_referral(user_data, prev_user)

        return Output(
            output_details=Common.jsonify(user_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
