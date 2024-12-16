from bson import ObjectId
from datetime import datetime, timedelta
from shared.models.common import Common
from shared.db.schedules import get_schedules_collection
from shared.models.constants import TimeFormats, OutputStatus
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

        new_data = Common.filter_none_values(new_data)
        return new_data

    def get_old_data(self) -> dict:
        query = {"_id": ObjectId(self.input._id)}
        old_data = self.schedules_collection.find_one(query)
        return old_data

    def check_expert_availability(self, expert_id: ObjectId, job_time: datetime) -> bool:
        time_window = 15 * 60
        start_time = job_time - timedelta(seconds=time_window)
        end_time = job_time + timedelta(seconds=time_window)

        query = {
            "expert_id": expert_id,
            "isDeleted": {"$ne": True},
            "job_time": {"$gte": start_time, "$lte": end_time}
        }
        conflict = self.schedules_collection.find_one(query)
        return conflict is not None

    def compute(self) -> Output:
        if self.input.expert_id:
            self.input.expert_id = ObjectId(self.input.expert_id)
            self.input.job_time = datetime.strptime(
                self.input.job_time, TimeFormats.AWS_TIME_FORMAT)
            if self.check_expert_availability(self.input.expert_id, self.input.job_time):
                return Output(
                    output_status=OutputStatus.FAILURE,
                    output_message="Expert is not available at this time"
                )

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
