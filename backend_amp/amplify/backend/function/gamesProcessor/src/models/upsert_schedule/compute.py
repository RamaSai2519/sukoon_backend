from bson import ObjectId
from datetime import datetime
from shared.models.common import Common
from shared.models.constants import TimeFormats
from shared.db.schedules import get_schedules_collection
from shared.models.interfaces import UpsertScheduleInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.schedules_collection = get_schedules_collection()

    def prep_data(self, new_data: dict, old_data: dict = None) -> dict:
        if self.input.isDeleted:
            return {"_id": ObjectId(self.input._id), "isDeleted": True}

        new_data.pop('_id', None)
        if old_data:
            mutable_fields = ['job_time', 'job_type', 'status',
                              'user_requested', 'reschedule_id']
            for field, value in old_data.items():
                if field in mutable_fields:
                    new_data[field] = value

        object_fields = ['user_id', 'expert_id']
        for field in object_fields:
            if isinstance(new_data.get(field), str):
                new_data[field] = ObjectId(new_data[field])

        if isinstance(new_data.get('job_time'), str):
            new_data['job_time'] = datetime.strptime(
                new_data['job_time'], TimeFormats.AWS_TIME_FORMAT)

        new_data = Common.filter_none_values(new_data)
        return new_data

    def get_old_data(self) -> dict:
        query = {"_id": ObjectId(self.input._id)}
        old_data = self.schedules_collection.find_one(query)
        return old_data

    def compute(self) -> Output:
        if self.input._id:
            old_data = self.get_old_data()
            new_data = self.prep_data(self.input.__dict__, old_data)
            new_data['updated_at'] = datetime.now()
            self.schedules_collection.update_one(
                {"_id": ObjectId(self.input._id)}, {"$set": new_data})
            return Output(
                output_details=Common.jsonify(new_data),
                output_message="Schedule updated successfully"
            )
        else:
            new_data = self.prep_data(self.input.__dict__)
            new_data['created_at'] = datetime.now()
            self.schedules_collection.insert_one(new_data)
            return Output(
                output_details=Common.jsonify(new_data),
                output_message="Schedule created successfully"
            )
