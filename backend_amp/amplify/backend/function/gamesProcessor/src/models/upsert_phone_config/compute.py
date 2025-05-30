from bson import ObjectId
from dataclasses import asdict
from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.db.users import get_phone_configs_collection
from shared.models.interfaces import PhoneConfigInput as Input, Output, PhoneConfig


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.configs_collection = get_phone_configs_collection()

    def pop_immutable_fields(self, new_data: dict) -> dict:
        fields = ["_id", "user_id", "createdAt", "source"]
        for field in fields:
            new_data.pop(field, None)
        return new_data

    def merge_old_data(self, new_data: dict, old_data: dict) -> dict:
        for key, value in old_data.items():
            if key not in new_data or new_data[key] is None or new_data[key] == "" or new_data[key] == []:
                new_data[key] = value
        return new_data

    def prep_data(self, new_data: dict, old_data: dict = None) -> dict:
        new_data = {k: v for k, v in new_data.items() if v is not None}
        if old_data:
            new_data = self.pop_immutable_fields(new_data)
            new_data = self.merge_old_data(new_data, old_data)
            new_data["updatedAt"] = Common.get_current_utc_time()
        else:
            new_data["createdAt"] = Common.get_current_utc_time()
            new_data["user_id"] = ObjectId(self.input.user_id)
        return new_data

    def get_old_data(self, user_id: str) -> PhoneConfig:
        query = {"user_id": ObjectId(user_id)}
        old_data = self.configs_collection.find_one(query)
        if not old_data:
            return None
        old_data = Common.clean_dict(old_data, PhoneConfig)
        return PhoneConfig(**old_data)

    def compute(self) -> Output:
        new_data = asdict(self.input)
        old_data = self.get_old_data(self.input.user_id)

        message = "Phone config Upsert failed"
        if old_data:
            new_data = self.prep_data(new_data, asdict(old_data))
            self.configs_collection.update_one(
                {"_id": old_data._id}, {"$set": new_data})
            message = "Phone config updated successfully"
        else:
            new_data = self.prep_data(new_data)
            self.configs_collection.insert_one(new_data)
            message = "Phone config inserted successfully"

        return Output(
            output_details=Common.jsonify(new_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
