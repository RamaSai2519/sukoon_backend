from bson import ObjectId
from pymongo.collection import Collection
from shared.models.constants import OutputStatus, meta_fields
from shared.db.users import get_user_collection, get_meta_collection
from shared.models.interfaces import UpsertEngagementDataInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_user_collection()
        self.meta_collection = get_meta_collection()

    def update_data(self, collection: Collection, filter_field: str, filter_value: str, update_data: dict, insert_data: dict = None) -> Output:
        update = collection.update_one(
            {filter_field: ObjectId(filter_value)}, {"$set": update_data}
        )

        if update.modified_count == 0 and insert_data:
            insert_result = collection.insert_one(insert_data)
            if insert_result.inserted_id is None:
                return Output(
                    output_details={},
                    output_status=OutputStatus.FAILURE,
                    output_message="Something went wrong"
                )

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message="Data updated successfully"
        )

    def update_meta_data(self, user_id: str, user_field: str, user_value: str) -> Output:
        query = {"user": ObjectId(user_id)}
        prev_meta: dict = self.meta_collection.find_one(query)
        if prev_meta and prev_meta.get(user_field) == user_value:
            return Output(
                output_details={},
                output_status=OutputStatus.SUCCESS,
                output_message="Value already exists"
            )

        return self.update_data(
            collection=self.meta_collection,
            filter_field="user",
            filter_value=user_id,
            update_data={user_field: user_value},
            insert_data={"user": ObjectId(user_id), user_field: user_value}
        )

    def update_user_data(self, user_id: str, user_field: str, user_value: str) -> Output:
        return self.update_data(
            collection=self.collection,
            filter_field="_id",
            filter_value=user_id,
            update_data={user_field: user_value}
        )

    def compute(self) -> Output:
        user_id = self.input.key
        user_field = self.input.field
        user_value = self.input.value

        if user_field in meta_fields:
            return self.update_meta_data(user_id, user_field, user_value)
        else:
            return self.update_user_data(user_id, user_field, user_value)
