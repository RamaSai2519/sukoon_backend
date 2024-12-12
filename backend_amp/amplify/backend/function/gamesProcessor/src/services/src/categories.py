import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.upsert_category.main import UpsertPlatformCategory
from models.list_platform_categories.main import ListPlatformCategories
from shared.models.interfaces import UpsertPlatformCategoryInput, ListPlatformCategoriesInput


class PlatformCategoryService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertPlatformCategoryInput(**input)
        output = UpsertPlatformCategory(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = ListPlatformCategoriesInput(**input_params)
        output = ListPlatformCategories(input).process()
        output = dataclasses.asdict(output)

        return output
 