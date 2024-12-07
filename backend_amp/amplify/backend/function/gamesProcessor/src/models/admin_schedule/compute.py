import json
from bson import ObjectId
from typing import List, Dict
from shared.models.common import Common
from shared.helpers.base import call_graphql
from shared.db.schedules import get_schedules_collection
from shared.models.constants import OutputStatus, scheduledJobStatuses
from shared.models.interfaces import GetScheduledJobsInput as Input, Output, Schedule


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.collection = get_schedules_collection()

    def format_schedules(self, schedules: List[Dict]):
        for schedule in schedules:
            request_meta: str = schedule.get('requestMeta', None)
            user_requested = schedule.get('user_requested', None)
            if request_meta is not None:
                request_meta: dict = json.loads(request_meta)

                expert_id = request_meta.get('expertId')
                schedule['expert'] = self.common.get_expert_name(
                    ObjectId(expert_id)) if expert_id else None

                user_id = request_meta.get('userId')
                schedule['user'] = self.common.get_user_name(
                    ObjectId(user_id)) if user_id else None
                schedule['initiatedBy'] = request_meta.get('initiatedBy', '')

            schedule['datetime'] = schedule.get('scheduledJobTime')
            schedule['source'] = Common.get_call_source(user_requested)
        return {'data': schedules}

    def get_dynamo_schedules(self) -> dict:
        query = '''
        query MyQuery($limit: Int = 1000, $scheduledJobStatus: ScheduledJobStatus = PENDING, $attributeExists: Boolean = false) {
            scheduledJobsByStatusAndTime(limit: $limit, sortDirection: DESC, scheduledJobStatus: $scheduledJobStatus, filter: {isDeleted: {attributeExists: $attributeExists}}) {
                items {
                    id
                    status
                    isDeleted
                    requestMeta
                    user_requested
                    scheduledJobStatus
                    scheduledJobTime
                }
            }
        }
        '''

        params = {'limit': 100}
        params['attributeExists'] = True if self.input.isDeleted == 'true' else False
        all_items = []

        for status in scheduledJobStatuses:
            params['scheduledJobStatus'] = status
            response = call_graphql(
                query=query, params=params, message='get_scheduled_jobs')
            if (type(response) == dict):
                all_items.extend(
                    response['scheduledJobsByStatusAndTime']['items'])
            else:
                print(response)

        formatted_response = self.format_schedules(all_items)

        return formatted_response

    def __format__(self, schedules: list) -> list:
        for schedule in schedules:
            job = Common.clean_dict(schedule, Schedule)
            job = Schedule(**job)

            if job.expert_id:
                schedule['expert'] = self.common.get_expert_name(job.expert_id)
            if job.user_id:
                schedule['user'] = self.common.get_user_name(job.user_id)

            schedule['datetime'] = job.job_time
            schedule['source'] = Common.get_call_source(job.user_requested)
            schedule = Common.jsonify(schedule)

        return schedules

    def prep_query(self) -> dict:
        query = {'isDeleted': True if self.input.isDeleted == 'true' else False}
        if self.input.filter_field == 'expert':
            filter_query = self.common.get_filter_query(
                'name', self.input.filter_value)
            experts = list(self.common.experts_collection.find(filter_query))
            expert_ids = [expert['_id'] for expert in experts]
            return {'expert_id': {'$in': expert_ids}, **query}

        elif self.input.filter_field == 'user':
            filter_query = self.common.get_filter_query(
                'name', self.input.filter_value)
            users = list(self.common.users_collection.find(filter_query))
            user_ids = [user['_id'] for user in users]
            return {'user_id': {'$in': user_ids}, **query}

        else:
            filter_query = self.common.get_filter_query(
                self.input.filter_field, self.input.filter_value)
            return {**filter_query, **query}

    def get_schedules(self) -> list:
        query = self.prep_query()
        print(query, 'query')
        cursor = self.collection.find(query).sort('job_time', -1)
        cursor = Common.paginate_cursor(cursor, int(
            self.input.page), int(self.input.size))
        total_count = self.collection.count_documents(query)

        return {'data': self.__format__(list(cursor)), 'total': total_count}

    def compute(self) -> Output:
        if self.input.old == 'true':
            response = self.get_dynamo_schedules()
        else:
            response = self.get_schedules()

        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message='Data received successfully'
        )
