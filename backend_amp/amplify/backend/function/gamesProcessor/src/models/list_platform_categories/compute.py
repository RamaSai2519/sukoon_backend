from bson import ObjectId
from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.models.interfaces import ListPlatformCategoriesInput as Input, Output
from shared.db.categories import get_platform_categories_collection, get_platform_sub_categories_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def format_categories(self, categories: list) -> list:
        query = {
            'category_id': {'$in': [category['_id'] for category in categories]}
        }
        collection = get_platform_sub_categories_collection()
        sub_categories = collection.find(query)

        for category in categories:
            category['sub_categories'] = [
                sub_category for sub_category in sub_categories if sub_category['category_id'] == category['_id']]
            category = Common.jsonify(category)
        return categories

    def compute(self) -> Output:
        query = {}
        if self.input.name:
            query['name'] = self.input.name
        elif self.input._id:
            query['_id'] = ObjectId(self.input._id)
        if self.input.type == 'main':
            collection = get_platform_categories_collection()
            categories = collection.find(query)
            categories = self.format_categories(list(categories))
        elif self.input.type == 'sub':
            collection = get_platform_sub_categories_collection()
            categories = collection.find(query)
            categories = Common.jsonify(list(categories))

        return Output(
            output_details={'data': categories, 'total': len(categories)},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched data"
        )
