from typing import Union
from bson import ObjectId
from models.common import Common
from pymongo.collection import Collection
from models.constants import OutputStatus
from models.interfaces import Output, SaveRemarkInput as Input
from db.events import get_event_users_collection, get_become_saarthis_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.filter = {"_id": ObjectId(self.input.key)}
        self.events_collection = get_event_users_collection()
        self.applicants_collection = get_become_saarthis_collection()
        self.collections = [self.events_collection, self.applicants_collection]

    def get_document(self, collection: Collection) -> Union[dict, None]:
        return collection.find_one(self.filter)

    def update_document(self, collection: Collection, update: dict) -> None:
        update_document = {"$set": update}
        collection.update_one(self.filter, update_document)

    def compute(self) -> Output:
        update_fields = {"remarks": self.input.value}
        for collection in self.collections:
            if self.get_document(collection):
                self.update_document(collection, update_fields)
                updated_document = self.get_document(collection)
                return Output(
                    output_details=Common.jsonify(updated_document),
                    output_status=OutputStatus.SUCCESS,
                    output_message="Successfully saved remark"
                )

        return Output(
            output_details={},
            output_status=OutputStatus.FAILURE,
            output_message="User not found"
        )
