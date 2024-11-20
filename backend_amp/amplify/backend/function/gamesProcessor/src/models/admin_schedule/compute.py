import json
from bson import ObjectId
from typing import List, Dict
from models.common import Common
from helpers.base import call_graphql
from models.constants import OutputStatus
from db.calls import get_schedules_collection
from models.interfaces import GetScheduledJobsInput as Input, Output


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

    def get_dynamo_schedules(self):
        query = '''
            query MyQuery($limit: Int = 100, $nextToken: String) {
                listScheduledJobs(limit: $limit, nextToken: $nextToken) {
                    nextToken
                    items {
                        id
                        status
                        isDeleted
                        requestMeta
                        user_requested
                        scheduledJobTime
                        scheduledJobStatus
                    }
                }
            }
        '''

        params = {'limit': 100}
        all_items = []
        response = call_graphql(
            query=query, params=params, message='get_scheduled_jobs')
        all_items.extend(response['listScheduledJobs']['items'])

        formatted_response = self.format_schedules(all_items)

        return formatted_response

    def compute(self) -> Output:
        response = self.get_dynamo_schedules()

        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message='Data received successfully'
        )
