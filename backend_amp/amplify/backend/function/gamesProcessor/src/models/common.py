from db.events import get_event_users_collection, get_events_collection
from db.calls import get_calls_collection, get_schedules_collection
from models.constants import calls_exclusion_projection
from db.referral import get_user_referral_collection
from flask_jwt_extended import get_jwt_identity
from db.experts import get_experts_collections
from db.calls import get_callsmeta_collection
from db.users import get_user_collection
from configs import CONFIG as config
from datetime import datetime, date
from pymongo.cursor import Cursor
from typing import List, Dict
from bson import ObjectId
import boto3
import pytz
import json
import re


class Common:
    def __init__(self):
        self.users_cache = {}
        self.images_cache = {}
        self.experts_cache = {}
        self.current_time = datetime.now()
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()
        self.events_collection = get_events_collection()
        self.experts_collection = get_experts_collections()
        self.schedules_collection = get_schedules_collection()
        self.callsmeta_collection = get_callsmeta_collection()
        self.referrals_collection = get_user_referral_collection()

    @staticmethod
    def get_identity() -> str:
        return get_jwt_identity()

    @staticmethod
    def get_s3_client() -> boto3.client:
        return boto3.client(
            "s3",
            region_name=config.REGION,
            aws_access_key_id=config.ACCESS_KEY,
            aws_secret_access_key=config.SECRET_ACCESS_KEY
        )

    @staticmethod
    def jsonify(doc: dict) -> dict:
        if not doc:
            return doc
        for field, value in doc.items():
            if isinstance(value, ObjectId):
                doc[field] = str(value)
            elif isinstance(value, datetime):
                if value.tzinfo is None:
                    value = value.replace(tzinfo=pytz.utc)
                doc[field] = value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return doc

    @staticmethod
    def string_to_date(doc: dict, field: str) -> date:
        if field in doc and doc[field] is not None and isinstance(doc[field], str):
            try:
                doc[field] = datetime.strptime(
                    doc[field], '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                doc[field] = datetime.now(pytz.utc)
        return doc[field]

    @staticmethod
    def duration_str_to_seconds(duration: str) -> int:
        if not duration:
            return 0
        duration = duration.split(':')
        hours, minutes, seconds = map(int, duration)
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def seconds_to_duration_str(seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        formatted_duration = []
        if hours > 0:
            formatted_duration.append(f'{int(hours)}h')

        if minutes > 0:
            formatted_duration.append(f'{int(minutes)}m')

        if seconds > 0:
            formatted_duration.append(f'{int(seconds)}s')

        return ' '.join(formatted_duration) if formatted_duration else '0s'

    @staticmethod
    def array_to_string(arr: list) -> str:
        return ', '.join(arr)

    @staticmethod
    def paginate_cursor(cursor: Cursor, page: int, size: int) -> Cursor:
        offset = (page - 1) * size
        if offset < 0:
            offset = 0
        return cursor.skip(offset).limit(size)

    @staticmethod
    def get_today_query(field: str = 'initiatedTime', local: bool = True) -> dict:
        current_date = datetime.now(pytz.timezone(
            'Asia/Kolkata')) if local else datetime.now()
        today_start = datetime.combine(current_date, datetime.min.time())
        today_end = datetime.combine(current_date, datetime.max.time())
        return {field: {'$gte': today_start, '$lt': today_end}}

    @staticmethod
    def clean_dict(doc: dict, dataClass) -> dict:
        if doc:
            document_fields = set(dataClass.__annotations__.keys())
            doc = {k: v for k, v in doc.items() if k in document_fields}
        return doc

    @staticmethod
    def get_call_status(calls_done: int) -> str:
        status_messages = {
            0: 'First call Pending',
            1: 'First call Done',
            2: 'Second call Done',
            3: 'Third call Done'
        }
        return status_messages.get(calls_done, 'Engaged')

    @staticmethod
    def get_call_source(user_requested: bool) -> str:
        if user_requested == True:
            return 'User Requested'
        elif user_requested == False:
            return 'Sukoon Initiated'
        else:
            return 'User Initiated'

    @staticmethod
    def get_filter_query(filter_field: str, filter_value: str) -> dict:
        if filter_field and filter_value:
            return {filter_field: {'$regex': filter_value, '$options': 'i'}}
        return {}

    def get_user_name(self, user_id: ObjectId) -> str:
        users_cache = self.users_cache
        if user_id not in users_cache:
            user = self.users_collection.find_one(
                {'_id': user_id}, {'name': 1})
            users_cache[user_id] = (
                user['name'] if user and 'name' in user else 'Unknown'
            )
        return users_cache[user_id]

    def get_expert_name(self, expert_id: ObjectId) -> str:
        experts_cache = self.experts_cache
        if expert_id not in experts_cache:
            expert = self.experts_collection.find_one(
                {'_id': expert_id}, {'name': 1})
            experts_cache[expert_id] = (
                expert['name'] if expert and 'name' in expert else 'Unknown'
            )
        return experts_cache[expert_id]

    def get_expert_image(self, expert_id: ObjectId) -> str:
        images_cache = self.images_cache
        if expert_id not in images_cache:
            expert = self.experts_collection.find_one(
                {'_id': expert_id}, {'profile': 1})
            print(expert)
            images_cache[expert_id] = (
                expert['profile'] if expert and 'profile' in expert else ''
            )
        return images_cache[expert_id]

    def format_calls(self, calls: List[Dict], req_names: bool = True) -> list:
        for call in calls:
            if req_names:
                call['user_id'] = call.get('user')
                call['expert_id'] = call.get('expert')
                call['user'] = self.get_user_name(
                    ObjectId(call.get('user'))) if call.get('user') else 'Unknown'
                call['expert'] = self.get_expert_name(
                    ObjectId(call.get('expert'))) if call.get('expert') else 'Unknown'
                call['expert_image'] = self.get_expert_image(
                    ObjectId(call.get('expert_id'))) if call.get('expert_id') else ''

            # Handle call source
            user_requested = call.get('user_requested', None)
            call['source'] = self.get_call_source(user_requested)

            # Convert the call to JSON
            call = Common.jsonify(call)

        return calls

    def get_events_history(self, query: dict) -> list:
        event_slugs = list(
            get_event_users_collection().distinct('source', query))
        query = {'slug': {'$in': event_slugs}}
        events = list(self.events_collection.find(query))
        events = [Common.jsonify(event) for event in events]
        return events

    def get_referrals(self, query: dict) -> list:
        referrals = list(self.referrals_collection.find(query))
        referrals = [Common.jsonify(referral) for referral in referrals]
        return referrals

    def get_schedules(self, query: dict) -> list:
        schedules = list(self.schedules_collection.find(query))
        schedules = self.format_calls(schedules)
        return schedules

    def get_schedules_counts(self, query: dict) -> dict:
        statuses = ['pending', 'completed', 'missed']
        counts = {}
        for status in statuses:
            query['status'] = status
            counts[status] = self.schedules_collection.count_documents(query)
        return counts

    def get_calls(self, query: dict = {}, projection: dict = {}, exclude: bool = True, format: bool = True, page: int = 0, size: int = 0, req_names: bool = True) -> list:
        if exclude:
            projection = {**projection, **calls_exclusion_projection}

        calls = self.calls_collection.find(
            query, projection).sort('initiatedTime', -1)

        if page > 0 and size > 0:
            calls = self.paginate_cursor(calls, page, size)

        elif size > 0:
            calls = calls.limit(size)

        if format:
            calls = self.format_calls(list(calls), req_names)

        return calls

    def get_internal_expertids(self) -> list:
        query = {'type': 'internal'}
        projection = {'_id': 1}
        experts = list(self.experts_collection.find(query, projection))
        return [expert.get('_id', '') for expert in experts]

    def get_internal_exclude_query(self, internal: str = '', field: str = 'expert') -> list:
        querier = '$in' if internal == 'true' else '$nin'
        internal_expert_ids = self.get_internal_expertids()
        return {field: {querier: internal_expert_ids}}

    def populate_call_meta(self, call: dict) -> dict:
        call_meta: dict = self.callsmeta_collection.find_one(
            {'callId': call['callId']}
        )
        if call_meta:
            for key, value in call_meta.items():
                if key not in call:
                    call[key] = value
        return call

    def extract_json(self, json_str: str) -> dict:
        def clean_json(json_str: str) -> str:
            json_str = json_str.replace("\n", "").replace(
                "```", "").replace("json", "").strip()
            return json_str

        try:
            if "json" in json_str:
                match = re.search(r'```json\n(.*?)```', json_str, re.DOTALL)
                if match:
                    response_text = clean_json(match.group(1))
                    response_text = json.loads(response_text)
                    return response_text
            cleaned_json_str = clean_json(json_str)
            cleaned_json_str = json.loads(cleaned_json_str)
            return cleaned_json_str
        except Exception as e:
            print(f"JSON Error: {str(e)}")
            return {}
