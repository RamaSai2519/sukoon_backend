from db.calls import get_calls_collection, get_schedules_collection
from models.constants import calls_exclusion_projection
from db.referral import get_user_referral_collection
from models.interfaces import User, EventUser, Call
from db.events import get_event_users_collection
from flask_jwt_extended import get_jwt_identity
from db.experts import get_experts_collections
from db.calls import get_callsmeta_collection
from db.users import get_user_collection
from datetime import datetime, date
from pymongo.cursor import Cursor
from typing import List, Dict
from bson import ObjectId
import pytz


class Common:
    def __init__(self):
        self.users_cache = {}
        self.experts_cache = {}
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()
        self.experts_collection = get_experts_collections()
        self.schedules_collection = get_schedules_collection()
        self.callsmeta_collection = get_callsmeta_collection()
        self.referrals_collection = get_user_referral_collection()

    @staticmethod
    def get_identity() -> str:
        return get_jwt_identity()

    @staticmethod
    def jsonify(doc: dict) -> dict:
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
            doc[field] = datetime.strptime(doc[field], '%Y-%m-%dT%H:%M:%S.%fZ')
        return doc[field]

    @staticmethod
    def duration_str_to_seconds(duration: str) -> int:
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

    def format_calls(self, calls: List[Dict], req_names: bool = True) -> list:
        for call in calls:
            # Fetch names if requested
            if req_names:
                call['user'] = self.get_user_name(
                    ObjectId(call.get('user'))) if call.get('user') else 'Unknown'
                call['expert'] = self.get_expert_name(
                    ObjectId(call.get('expert'))) if call.get('expert') else 'Unknown'

            # Handle call source
            user_requested = call.get('user_requested', None)
            call['source'] = self.get_call_source(user_requested)

            # Convert the call to JSON
            call = Common.jsonify(call)

        return calls

    def get_events_history(self, query: dict) -> list:
        events = list(get_event_users_collection().find(query))
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

    def get_internal_exclude_query(self, internal: str = '', field: str = 'expert') -> list:
        query = {'type': 'internal'}
        querier = '$in' if internal == 'true' else '$nin'
        projection = {'_id': 1}
        experts = list(self.experts_collection.find(query, projection))
        internal_expert_ids = [expert.get('_id', '') for expert in experts]
        return {field: {querier: internal_expert_ids}}

    def populate_call_meta(self, call: dict) -> dict:
        call_meta: dict = self.callsmeta_collection.find_one(
            {'callId': call['callId']}
        )
        if call_meta:
            for key, value in call_meta.items():
                call[key] = value
        return call
