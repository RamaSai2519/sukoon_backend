from shared.models.interfaces import GetUsersInput as Input, Output
from shared.models.constants import OutputStatus, TimeFormats
from shared.db.events import get_event_users_collection
from shared.db.calls import get_calls_collection
from shared.db.users import get_user_collection
from shared.helpers.users import UsersHelper
from pymongo.collection import Collection
from shared.models.common import Common
from datetime import datetime
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.helper = UsersHelper()
        self.collection = get_user_collection()
        self.calls_collection = get_calls_collection()
        self.events_collection = get_event_users_collection()

    def filter_last_reached(self, collection: Collection, filter_field: str, distinct_field: str) -> list:
        query = {}
        if self.input.last_reached_type == 'call':
            query['status'] = self.input.call_status or 'successful'

        user_ids = []
        self.input.last_reached_from = datetime.strptime(
            self.input.last_reached_from, TimeFormats.ANTD_TIME_FORMAT
        )
        self.input.last_reached_till = datetime.strptime(
            self.input.last_reached_till, TimeFormats.ANTD_TIME_FORMAT
        )
        query[filter_field] = {
            '$gte': self.input.last_reached_from,
            '$lte': self.input.last_reached_till
        }
        user_ids = collection.distinct(distinct_field, query)
        return user_ids

    def handle_number_of_calls(self, user_ids: list) -> list:
        call_counts = {}
        query = {'user': {'$in': user_ids}}
        if self.input.call_status:
            query['status'] = self.input.call_status
        calls = self.calls_collection.find(query)
        for user_id in user_ids:
            call_counts[user_id] = 0

        for call in calls:
            user_id = call['user']
            if user_id in call_counts:
                call_counts[user_id] += 1

        call_count_map = {}
        for user_id, count in call_counts.items():
            if count not in call_count_map:
                call_count_map[count] = []
            if user_id not in call_count_map[count]:
                call_count_map[count].append(user_id)

        return call_count_map.get(int(self.input.number_of_calls), [])

    def compute(self) -> Output:
        query = {}
        if self.input.phoneNumber is not None or self.input.user_id is not None:
            users = self.helper.get_user(
                self.input.phoneNumber, self.input.user_id, self.input.internal, self.input.call_status)
            if not users:
                return Output(
                    output_details={},
                    output_status=OutputStatus.FAILURE,
                    output_message="User not found"
                )
        else:
            user_ids = []
            if self.input.last_reached_type:
                if self.input.last_reached_type == 'call':
                    user_ids = self.filter_last_reached(
                        self.calls_collection, 'initiatedTime', 'user')
                elif self.input.last_reached_type == 'event':
                    user_ids = self.filter_last_reached(
                        self.events_collection, 'updatedAt', 'userId')
                elif self.input.last_reached_type == 'both':
                    call_user_ids = self.filter_last_reached(
                        self.calls_collection, 'initiatedTime', 'user')
                    event_user_ids = self.filter_last_reached(
                        self.events_collection, 'updatedAt', 'userId')
                    user_ids = list(set(call_user_ids + event_user_ids))

            if self.input.number_of_calls:
                user_ids = self.handle_number_of_calls(user_ids)

            query = Common.get_filter_query(
                self.input.filter_field, self.input.filter_value)
            object_id_fields = ['_id', 'lastModifiedBy']
            if self.input.filter_field in object_id_fields:
                query[self.input.filter_field] = ObjectId(
                    self.input.filter_value)
            date_fields = ['createdDate', 'birthDate']
            if self.input.filter_field in date_fields:
                query[self.input.filter_field] = self.input.filter_value
                if self.input.filter_value == 'null':
                    query[self.input.filter_field] = {
                        '$or': [
                            {self.input.filter_field: None},
                            {self.input.filter_field: {'$exists': False}},
                            {self.input.filter_field: datetime.strptime(
                                '0001-01-01', '%Y-%m-%d')}
                        ]
                    }
            bool_fields = ['isDeleted', 'profileCompleted', 'isPaidUser',
                           'wa_opt_out', 'isBlocked', 'isBusy', 'active']
            if self.input.filter_field in bool_fields:
                query[self.input.filter_field] = True if self.input.filter_value == 'true' else False

            if self.input.joined_from and self.input.joined_till:
                query['createdDate'] = {
                    '$gte': datetime.strptime(self.input.joined_from, TimeFormats.ANTD_TIME_FORMAT),
                    '$lte': datetime.strptime(self.input.joined_till, TimeFormats.ANTD_TIME_FORMAT)
                }
            if user_ids != []:
                query['_id'] = {'$in': user_ids}
            users = self.helper.get_users(
                self.input.size, self.input.page, query)

        total = self.collection.count_documents(query)

        return Output(
            output_details=users,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched user(s)" +
            f" ({total}: total)"
        )
