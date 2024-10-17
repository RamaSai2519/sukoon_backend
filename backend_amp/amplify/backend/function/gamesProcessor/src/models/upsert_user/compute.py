import json
import string
import random
import hashlib
import requests
import dataclasses
from datetime import datetime
from typing import Union, Tuple
from models.common import Common
from configs import CONFIG as config
from db.users import get_user_collection
from models.upsert_user.slack import SlackManager
from models.interfaces import User as Input, Output
from db.referral import get_user_referral_collection
from models.constants import OutputStatus, application_json_header


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.slack_manager = SlackManager()
        self.users_collection = get_user_collection()
        self.referrals_collection = get_user_referral_collection()

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

    def merge_old_data(self, user_data: dict, prev_user: dict) -> dict:
        for key, value in prev_user.items():
            if key not in user_data or user_data[key] is None or user_data[key] == '':
                user_data[key] = value
        return user_data

    def pop_immutable_fields(self, user_data: dict) -> dict:
        fields = ['_id', 'phoneNumber', 'refCode', 'createdDate']
        for field in fields:
            user_data.pop(field, None)
        return user_data

    def prep_data(self, user_data: dict, prev_user: dict = None) -> dict:
        if prev_user:
            user_data = self.pop_immutable_fields(user_data)
            user_data = self.merge_old_data(user_data, prev_user)
        else:
            user_data = self.defaults(user_data)
        user_data.pop('refCode', None)

        user_data['profileCompleted'] = bool(
            user_data.get('name') and user_data.get('city') and user_data.get('birthDate'))

        if user_data.get('profileCompleted') and (not prev_user or not prev_user.get('refCode')):
            user_data['refCode'] = self.generate_referral_code(
                user_data['name'], user_data['phoneNumber'])

        if isinstance(user_data.get('birthDate'), str):
            user_data['birthDate'] = Common.string_to_date(
                user_data, 'birthDate')

        user_data = {k: v for k, v in user_data.items() if v is not None}
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

    def validate_phoneNumber(self, phoneNumber: str) -> Union[dict, None]:
        user = self.users_collection.find_one({'phoneNumber': phoneNumber})
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
        self.users_collection.update_one(
            {'phoneNumber': user_data['phoneNumber']},
            {'$set': user_data}
        )

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
            user_name = user_data.get('name', None)
            user_number = user_data.get('phoneNumber')
            user_name = user_name if user_name else user_number
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
        user_name = user_data.get('name', None)
        user_number = user_data.get('phoneNumber')
        user_profile = user_data.get('profileCompleted', False)
        response = self.send_insert_message(
            user_name, user_number, user_profile)
        message += ' and sent welcome message' if response else ' but failed to send welcome message'

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
        self.update_user(user_data, prev_user)

    def send_insert_message(self, name: str, phone_number: str, profileCompleted: bool):
        if profileCompleted == False:
            pass
            # image_link = 'https://sukoon-media.s3.ap-south-1.amazonaws.com/wa_promo_image.jpeg'
            # payload = {'template_name': 'LEADS',
            #            'phone_number': phone_number, 'parameters': {'image_link': image_link}}
        else:
            payload = {'template_name': 'WELCOME_REGISTRATION',
                       'phone_number': phone_number,
                       'parameters': {'user_name': name if name else phone_number}}
        response = self.send_wa_message(payload)
        return response

    def compute(self) -> Output:
        user = self.input
        user_data = dataclasses.asdict(user)
        prev_user = self.validate_phoneNumber(user_data['phoneNumber'])

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
