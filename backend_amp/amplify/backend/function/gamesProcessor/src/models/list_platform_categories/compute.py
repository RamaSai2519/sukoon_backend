from bson import ObjectId
from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.models.interfaces import ListPlatformCategoriesInput as Input, Output
from shared.db.categories import get_platform_categories_collection, get_platform_sub_categories_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self) -> Output:
        query = {}
        if self.input.name:
            query['name'] = self.input.name
        elif self.input._id:
            query['_id'] = ObjectId(self.input._id)
        if self.input.type == 'main':
            collection = get_platform_categories_collection()
            categories = collection.find(query)
            categories = Common.jsonify(list(categories))
        elif self.input.type == 'sub':
            collection = get_platform_sub_categories_collection()
            categories = collection.find(query)
            categories = Common.jsonify(list(categories))

        return Output(
            output_details={'data': categories, 'total': len(categories)},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched data"
        )
