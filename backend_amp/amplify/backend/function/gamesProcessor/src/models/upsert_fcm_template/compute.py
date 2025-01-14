from shared.models.interfaces import UpsertFCMTemplateInput as Input, Output
from shared.models.constants import OutputStatus
from shared.db.users import get_fcm_templates_collection
from shared.models.common import Common
from bson import ObjectId

class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.templates_collection = get_fcm_templates_collection()

    def pop_immutable_fields(self, new_data: dict) -> dict:
        # Remove immutable fields that should not be updated
        fields = ["_id","createdAt"]
        for field in fields:
            new_data.pop(field, None)
        return new_data

    def merge_old_data(self, new_data: dict, old_data: dict) -> dict:
        # Merge old data into new data to fill in missing fields
        for key, value in old_data.items():
            if key not in new_data or new_data[key] is None or new_data[key] == "" or new_data[key] == []:
                new_data[key] = value
        return new_data

    def prep_data(self, new_data: dict, old_data: dict = None) -> dict:
        # Prepare the data for insertion or update
        if old_data:
            new_data = self.pop_immutable_fields(new_data)
            new_data = self.merge_old_data(new_data, old_data)
            new_data["updatedAt"] = Common.get_current_utc_time()
        else:
            new_data["createdAt"] = Common.get_current_utc_time()
            #new_data["user_id"] = ObjectId(self.input.user_id)
        new_data = {k: v for k, v in new_data.items() if v is not None}
        return new_data

    def get_old_data(self, name: str) -> dict:
        # Fetch old data by name
        query = {"name": name}
        old_data = self.templates_collection.find_one(query)
        if not old_data:
            return None
        return old_data

    def compute(self) -> Output:
        # Main compute logic
        new_data = self.input.__dict__  # Assuming input contains 'data' as a dictionary
        old_data = self.get_old_data(self.input.name)

        message = "FCM template upsert failed"
        if old_data:
            # Update existing entry
            new_data = self.prep_data(new_data, old_data)
            self.templates_collection.update_one(
                {"_id": old_data["_id"]}, {"$set": new_data}va
            )
            message = "FCM template updated successfully"
        else:
            # Insert new entry
            new_data = self.prep_data(new_data)
            self.templates_collection.insert_one(new_data)
            message = "FCM template inserted successfully"

        return Output(
            output_details=Common.jsonify(new_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
