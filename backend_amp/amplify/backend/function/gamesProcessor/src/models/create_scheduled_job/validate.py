from shared.models.interfaces import ScheduledJobInput as Input
from shared.models.constants import not_interested_statuses
from shared.db.users import get_meta_collection
from datetime import datetime
from bson import ObjectId
import json


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.meta_collection = get_meta_collection()

    def get_meta(self) -> dict:
        request_meta = json.loads(self.input.request_meta)
        user_id = ObjectId(request_meta.get('userId'))
        query = {"user": user_id}
        return self.meta_collection.find_one(query)

    def validate_mandatory_fields(self):
        mandatory_fields = ['job_time', 'job_type', 'status', 'request_meta']
        for field in mandatory_fields:
            if not getattr(self.input, field):
                return False, f"{field.replace('_', ' ').capitalize()} is mandatory"
        return True, ""

    def validate_job_time_and_status(self):
        try:
            datetime.strptime(self.input.job_time, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return False, "Job time is not a valid AWS time string"

        if self.input.status not in ['PENDING', 'WAPENDING']:
            return False, "Invalid status"

        return True, ""

    def validate_user(self) -> tuple:
        user_meta = self.get_meta()
        if not user_meta:
            return True, ""

        if user_meta.get("userStatus") in not_interested_statuses:
            return False, "User is not interested"

        return True, ""

    def validate_input(self):
        is_valid, message = self.validate_mandatory_fields()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_job_time_and_status()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_user()
        if not is_valid:
            return is_valid, message

        return True, ""
