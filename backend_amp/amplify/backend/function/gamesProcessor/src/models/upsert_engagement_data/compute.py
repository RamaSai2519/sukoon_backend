import requests
from bson import ObjectId
from shared.models.common import Common
from pymongo.collection import Collection
from shared.configs import CONFIG as config
from shared.db.users import get_meta_collection
from shared.models.constants import OutputStatus, meta_fields
from shared.models.interfaces import UpsertEngagementDataInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.meta_collection = get_meta_collection()

    def update_data(self, collection: Collection, filter_field: str, filter_value: str, update_data: dict, insert_data: dict = None) -> Output:
        update = collection.update_one(
            {filter_field: ObjectId(filter_value)}, {'$set': update_data}
        )

        if update.modified_count == 0 and insert_data:
            insert_result = collection.insert_one(insert_data)
            if insert_result.inserted_id is None:
                return Output(
                    output_details={},
                    output_status=OutputStatus.FAILURE,
                    output_message='Something went wrong'
                )

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message='Data updated successfully'
        )

    def update_meta_data(self, user_id: str, user_field: str, user_value: str) -> Output:
        query = {'user': ObjectId(user_id)}
        prev_meta: dict = self.meta_collection.find_one(query)
        if prev_meta and prev_meta.get(user_field) == user_value:
            return Output(output_message='Value already exists')

        return self.update_data(
            collection=self.meta_collection,
            filter_field='user',
            filter_value=user_id,
            update_data={user_field: user_value,
                         'updatedAt': Common.get_current_utc_time()},
            insert_data={'user': ObjectId(user_id), user_field: user_value,
                         'createdAt': Common.get_current_utc_time(),
                         'updatedAt': Common.get_current_utc_time()}
        )

    def update_user_data(self, user_id: str, user_field: str, user_value: str) -> Output:
        url = config.URL + '/actions/user'
        payload = {'_id': user_id, user_field: user_value}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return Output(output_message='Data updated successfully')
        else:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message='Something went wrong'
            )

    def compute(self) -> Output:
        user_id = self.input.key
        user_field = self.input.field
        user_value = self.input.value

        if user_field in meta_fields:
            return self.update_meta_data(user_id, user_field, user_value)
        else:
            return self.update_user_data(user_id, user_field, user_value)
