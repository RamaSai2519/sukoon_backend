from shared.models.interfaces import UpsertFCMTemplateInput as Input, Output
from shared.db.users import get_fcm_templates_collection
from shared.models.constants import OutputStatus
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.templates_collection = get_fcm_templates_collection()

    def pop_immutable_fields(self, new_data: dict) -> dict:
        fields = ["_id", "createdAt"]
        for field in fields:
            new_data.pop(field, None)
        return new_data

    def merge_old_data(self, new_data: dict, old_data: dict) -> dict:
        for key, value in old_data.items():
            if key not in new_data or new_data[key] is None or new_data[key] == "" or new_data[key] == []:
                new_data[key] = value
        return new_data

    def prep_data(self, new_data: dict, old_data: dict = None) -> dict:
        if old_data:
            new_data = self.pop_immutable_fields(new_data)
            new_data = self.merge_old_data(new_data, old_data)
        else:
            new_data["createdAt"] = Common.get_current_utc_time()
        new_data["updatedAt"] = Common.get_current_utc_time()
        new_data = {k: v for k, v in new_data.items() if v is not None}
        return new_data

    def get_old_data(self, name: str) -> dict:
        query = {"name": name}
        old_data = self.templates_collection.find_one(query)
        if not old_data:
            return None
        return old_data

    def compute(self) -> Output:
        new_data = self.input.__dict__
        old_data = self.get_old_data(self.input.name)

        message = "FCM template upsert failed"
        if old_data:
            new_data = self.prep_data(new_data, old_data)
            self.templates_collection.update_one(
                {"_id": old_data["_id"]}, {"$set": new_data}
            )
            message = "FCM template updated successfully"
        else:
            new_data = self.prep_data(new_data)
            self.templates_collection.insert_one(new_data)
            message = "FCM template inserted successfully"

        return Output(
            output_details=Common.jsonify(new_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
