from bson import ObjectId
from shared.models.common import Common
from shared.models.constants import OutputStatus
from flask_jwt_extended import jwt_required
from shared.db.experts import get_categories_collection
from shared.models.interfaces import CategoriesInput as Input, Output, Category


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_categories_collection()

    def get_categories(self) -> Output:
        projection = {"_id": 0, "name": 1}
        categories = list(self.collection.find({}, projection))
        categories = [category["name"] for category in categories]

        return Output(
            output_details=categories,
            output_status=OutputStatus.SUCCESS,
            output_message="Fetched categories successfully"
        )

    def validate_category(self) -> bool:
        query = {"name": self.input.name}
        prev_category = self.collection.find_one(query)
        return prev_category is not None

    @jwt_required()
    def insert_categories(self):
        category = self.input.name
        if self.validate_category():
            return Output(
                output_details={"name": category},
                output_status=OutputStatus.FAILURE,
                output_message="Category already exists"
            )

        admin_id = ObjectId(Common.get_identity())
        category_obj = Category(name=category, lastModifiedBy=admin_id)
        self.collection.insert_one(category_obj.__dict__)

        return Output(
            output_details={"name": category},
            output_status=OutputStatus.SUCCESS,
            output_message="Category added successfully"
        )

    def compute(self) -> Output:
        if self.input.action == "get":
            return self.get_categories()
        elif self.input.action == "post":
            return self.insert_categories()
