import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.upsert_category.main import UpsertPlatformCategory
from shared.models.interfaces import UpsertPlatformCategoryInput


class PlatformCategoryService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertPlatformCategoryInput(**input)
        output = UpsertPlatformCategory(input).process()
        output = dataclasses.asdict(output)

        return output
