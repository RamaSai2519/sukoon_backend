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
from models.upsert_user.slack import SlackManager
from shared.db.referral import get_user_referral_collection
from shared.db.whatsapp import get_whatsapp_templates_collection
from shared.models.interfaces import User as Input, Output, UserBalance
from shared.models.constants import OutputStatus, application_json_header, test_numbers
from shared.db.users import get_user_collection, get_subscription_plans_collection, get_user_balances_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.query = self.decide_query()
        self.slack_manager = SlackManager()
        self.users_collection = get_user_collection()
        self.balances_collection = get_user_balances_collection()
        self.referrals_collection = get_user_referral_collection()
        self.plans_collection = get_subscription_plans_collection()
        self.templates_collection = get_whatsapp_templates_collection()

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
        user_data['plan'] = 'default'
        user_data['isBlocked'] = False
        user_data['wa_opt_out'] = False
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

        if user_data.get('birthDate') in ['', None] and self.input.opt_age:
            user_data['birthDate'] = Common.calculate_dob(self.input.opt_age)

        user_data['profileCompleted'] = False
        man_fields = ['birthDate', 'city', 'name']
        if all(user_data.get(field) for field in man_fields):
            for field in man_fields:
                if user_data.get(field) not in ['', None]:
                    user_data['profileCompleted'] = True
                else:
                    user_data['profileCompleted'] = False
                    break

        if user_data.get('profileCompleted') and (not prev_user or not prev_user.get('refCode')):
            user_name = user_data.get('name', '') or ''
            user_number = user_data.get('phoneNumber')
            ref_code = self.generate_referral_code(user_name, user_number)
            user_data['refCode'] = ref_code

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

        if user_data.get('profileCompleted') == True and prev_user and prev_user.get('profileCompleted') == False:
            user_number = user_data.get('phoneNumber')
            user_name = user_data.get('name', user_number)
            dob = user_data.get('birthDate')
            response = self.send_insert_message(
                user_name, user_number, True, user_data.get('refSource'), dob)
            message = ' and sent welcome message' if response else ' but failed to send welcome message'
            if user_number not in test_numbers:
                message += self.slack_manager.send_message(
                    user_name, 'User', str(prev_user['_id']))

            return f'Successfully updated user{message}'

        return 'Successfully updated user'

    def insert_user(self, user_data: dict) -> Tuple[str, dict]:
        user_data['_id'] = self.users_collection.insert_one(
            user_data).inserted_id
        balance_doc = self.set_default_balances(user_data)
        print(balance_doc, '__balance_doc__')

        message = 'Successfully created user'
        user_number = user_data.get('phoneNumber')
        user_name = user_data.get('name', user_number)
        user_profile = user_data.get('profileCompleted', False)
        dob = user_data.get('birthDate')
        response = self.send_insert_message(
            user_name, user_number, user_profile, user_data.get('refSource'), dob)
        message += ' and sent welcome message' if response else ' but did not send welcome message'

        signup_type = 'User' if user_profile else 'Lead'
        if user_number not in test_numbers:
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

    def get_template_name(self, refSource: str, dob: datetime) -> str:
        if not refSource:
            return 'PROMO_TEMPLATE'

        refSource = refSource.upper()
        age = Common.calculate_age(dob) if dob else self.input.opt_age

        if age is not None and age < 50:
            template_name = f'{refSource}_SIGNUP_TEMPLATE_KIDS'
        else:
            template_name = f'{refSource}_SIGNUP_TEMPLATE'

        template = self.templates_collection.find_one(
            {'template_name': template_name})
        return template_name if template else 'PROMO_TEMPLATE'

    def send_insert_message(self, name: str, phone_number: str, profileCompleted: bool, refSource: str = None, dob: datetime = None) -> bool:
        template_name = self.get_template_name(refSource, dob)
        if template_name != 'PROMO_TEMPLATE':
            profileCompleted = True
        if profileCompleted == True:
            payload = {
                'template_name': template_name,
                'phone_number': phone_number,
                'request_meta': json.dumps({'user_name': name}),
                'parameters': {
                    # 'image_link': 'https://sukoon-media.s3.ap-south-1.amazonaws.com/wa_promo_image.jpeg'
                }
            }
            response = self.send_wa_message(payload)
            return response
        return None

    def set_default_balances(self, user_data: dict):
        query = {'name': user_data.get('plan', 'default')}
        plan = self.plans_collection.find_one(query)
        if not plan:
            plan = {
                'name': 'default',
                'price': 0,
                'free_events': 1000,
                'paid_events': 0,
                'sarathi_calls': 0,
                'expert_calls': 0,
            }
            self.plans_collection.insert_one(plan)
        plan['user'] = user_data['_id']
        balance_doc = Common.clean_dict(plan, UserBalance)
        balance_doc.pop('_id')
        self.balances_collection.insert_one(balance_doc)
        return balance_doc

    def compute(self) -> Output:
        user = self.input
        user_data = dataclasses.asdict(user)
        user_data.pop('opt_age')
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
