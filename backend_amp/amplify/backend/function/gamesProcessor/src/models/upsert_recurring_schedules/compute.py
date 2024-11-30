from bson import ObjectId
from datetime import datetime
from shared.models.common import Common
from shared.db.schedules import get_reschedules_collection
from shared.models.constants import OutputStatus, TimeFormats
from shared.models.interfaces import UpsertRecurringSchedulesInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.reschedules_collection = get_reschedules_collection()

    def prep_data(self, new_data: dict, old_data: dict = None) -> dict:
        if old_data:
            mutable_fields = ['job_expiry', 'job_time',
                              'job_type', 'frequency', 'days']
            for field, value in new_data.items():
                if field in mutable_fields:
                    old_data[field] = value

        if isinstance(old_data.get('job_time'), str):
            old_data['job_time'] = datetime.strptime(
                old_data['job_time'], TimeFormats.HOURS_24_FORMAT)

        if isinstance(old_data.get('job_expiry'), str):
            old_data['job_expiry'] = datetime.strptime(
                old_data['job_expiry'], TimeFormats.ANTD_TIME_FORMAT)

        object_fields = ['user_id', 'expert_id']
        for field in object_fields:
            if isinstance(old_data.get(field), str):
                old_data[field] = ObjectId(old_data[field])
        return old_data

    def get_old_data(self) -> dict:
        query = {"_id": ObjectId(self.input._id)}
        old_data = self.reschedules_collection.find_one(query)
        return old_data

    def compute(self) -> Output:
        if self.input._id:
            old_data = self.get_old_data()
            new_data = self.prep_data(self.input.__dict__, old_data)
            self.reschedules_collection.update_one(
                {"_id": ObjectId(self.input._id)}, {"$set": new_data})
            return Output(output_details=Common.jsonify(new_data),
                          output_message="Recurring schedule updated successfully")
        else:
            new_data = self.prep_data(self.input.__dict__)
            new_data['created_at'] = datetime.now()
            self.reschedules_collection.insert_one(new_data)
            return Output(output_details=Common.jsonify(new_data),
                          output_message="Recurring schedule created successfully")
