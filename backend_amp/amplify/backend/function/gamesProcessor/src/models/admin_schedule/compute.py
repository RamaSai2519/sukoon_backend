from bson import ObjectId
from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.db.schedules import get_schedules_collection
from shared.models.interfaces import GetScheduledJobsInput as Input, Output, Schedule


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.collection = get_schedules_collection()

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
        query['job_type'] = 'CALL'
        if self.input.pending == 'true':
            query['status'] = {'$in': ['PENDING', 'WAPENDING']}
        if self.input.fromToday == 'true':
            today = Common.get_current_utc_time()
            start_time = today.replace(hour=0, minute=0)
            query['job_time'] = {'$gte': start_time}
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

        elif self.input.filter_field in ['user_id', 'expert_id']:
            return {self.input.filter_field: ObjectId(self.input.filter_value), **query}

        else:
            filter_query = self.common.get_filter_query(
                self.input.filter_field, self.input.filter_value)
            return {**filter_query, **query}

    def get_schedules(self) -> list:
        query = self.prep_query()
        total_count = self.collection.count_documents(query)
        if total_count <= 10:
            self.input.page = 1
            self.input.size = total_count
        greatest_page = total_count // int(self.input.size)
        if int(self.input.page) > greatest_page:
            self.input.page = greatest_page + 1
        cursor = self.collection.find(query).sort('job_time', -1)
        cursor = Common.paginate_cursor(cursor, int(
            self.input.page), int(self.input.size))

        return {'data': self.__format__(list(cursor)), 'total': total_count}

    def compute(self) -> Output:
        response = self.get_schedules()

        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message='Data received successfully'
        )
