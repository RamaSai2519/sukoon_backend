from bson import ObjectId
from datetime import datetime
from shared.models.common import Common
from shared.models.constants import TimeFormats
from shared.db.schedules import get_reschedules_collection
from shared.models.interfaces import UpsertRecurringSchedulesInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.reschedules_collection = get_reschedules_collection()

    def pop_immutable_fields(self, new_data: dict) -> dict:
        fields = ["_id", "created_at", "user_id", "expert_id"]
        for field in fields:
            new_data.pop(field, None)
        return new_data

    def prep_data(self, new_data: dict, old_data: dict = None) -> dict:
        if old_data:
            new_data = self.pop_immutable_fields(new_data)
            new_data = {**old_data, **new_data}

        if isinstance(new_data.get('job_expiry'), str):
            new_data['job_expiry'] = datetime.strptime(
                new_data['job_expiry'], TimeFormats.ANTD_TIME_FORMAT)

        object_fields = ['user_id', 'expert_id']
        for field in object_fields:
            if isinstance(new_data.get(field), str):
                new_data[field] = ObjectId(new_data[field])

        if new_data.get('week_days'):
            new_data['week_days'] = list(
                map(lambda x: x.lower(), new_data['week_days']))

        if new_data.get('month_days'):
            new_data['month_days'] = list(
                map(int, new_data['month_days']))

        new_data.pop('_id', None)
        new_data = Common.filter_none_values(new_data)
        return new_data

    def get_old_data(self, query: dict) -> dict:
        return self.reschedules_collection.find_one(query)

    def compute(self) -> Output:
        if self.input._id:
            query = {"_id": ObjectId(self.input._id)}
            old_data = self.get_old_data(query)
            new_data = self.prep_data(self.input.__dict__, old_data)
            update = {"$set": new_data}
            self.reschedules_collection.update_one(query, update)
            return Output(
                output_details=Common.jsonify(new_data),
                output_message="Recurring schedule updated successfully"
            )
        else:
            new_data = self.prep_data(self.input.__dict__)
            new_data['created_at'] = datetime.now()
            self.reschedules_collection.insert_one(new_data)
            return Output(
                output_details=Common.jsonify(new_data),
                output_message="Recurring schedule created successfully"
            )
