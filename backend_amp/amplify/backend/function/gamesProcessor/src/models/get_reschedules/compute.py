from bson import ObjectId
from shared.models.common import Common
from shared.db.schedules import get_reschedules_collection
from shared.models.interfaces import GetReSchedulesInput as Input, Output, RecurringSchedule


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.collection = get_reschedules_collection()

    def prep_query(self) -> dict:
        query = {}
        if self.input._id:
            query['_id'] = ObjectId(self.input._id)
            return query

        if not self.input.expired == 'true':
            query['job_expiry'] = {'$gt': self.common.get_current_time()}
        else:
            query['job_expiry'] = {'$lt': self.common.get_current_time()}

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

        elif self.input.filter_field == 'job_expiry':
            return query

        else:
            filter_query = self.common.get_filter_query(
                self.input.filter_field, self.input.filter_value)

        return {**query, **filter_query}

    def __format__(self, schedules: list) -> list:
        for schedule in schedules:
            job = Common.clean_dict(schedule, RecurringSchedule)
            job = RecurringSchedule(**job)

            if job.user_id:
                schedule['user'] = self.common.get_user_name(job.user_id)
            if job.expert_id:
                schedule['expert'] = self.common.get_expert_name(job.expert_id)

            schedule = Common.jsonify(schedule)
        return schedules

    def compute(self) -> Output:
        query = self.prep_query()
        cursor = self.collection.find(query).sort('job_expiry', 1)
        cursor = Common.paginate_cursor(cursor, int(
            self.input.page), int(self.input.size))
        schedules = self.__format__(list(cursor))
        total = self.collection.count_documents(query)

        return Output(
            output_details={'data': schedules, 'total': total},
            output_message="Successfully fetched rescdule(s)"
        )
