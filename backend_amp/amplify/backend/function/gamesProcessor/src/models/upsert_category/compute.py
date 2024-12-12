from bson import ObjectId
from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.models.interfaces import UpsertPlatformCategoryInput as Input, Output
from shared.db.categories import get_platform_categories_collection, get_platform_sub_categories_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_platform_categories_collection()
        self.sub_collection = get_platform_sub_categories_collection()

    def get_category_id(self) -> ObjectId:
        query = {'name': self.input.name}
        doc = self.collection.find_one(query)
        if not doc:
            return None
        return doc['_id']

    def get_sub_category_id(self, query: dict) -> dict:
        doc = self.sub_collection.find_one(query)
        if not doc:
            return None
        return doc['_id']

    def create_category(self) -> ObjectId:
        doc = {'name': self.input.name}
        return self.collection.insert_one(doc).inserted_id

    def compute(self) -> Output:
        category_id = self.get_category_id()
        if not category_id:
            category_id = self.create_category()

        if self.input.icon:
            self.collection.update_one(
                {'_id': category_id},
                {'$set': {'icon': self.input.icon}}
            )

        output = {'category_id': category_id}

        if self.input.sub_category:
            doc = {
                'name': self.input.sub_category,
                'category_id': category_id
            }
            sub_category_id = self.get_sub_category_id(doc)
            if not sub_category_id:
                sub_category_id = self.sub_collection.insert_one(
                    doc).inserted_id

            output['sub_category_id'] = sub_category_id

        return Output(
            output_details=Common.jsonify(output),
            output_status=OutputStatus.SUCCESS,
            output_message='Category upserted successfully'
        )
