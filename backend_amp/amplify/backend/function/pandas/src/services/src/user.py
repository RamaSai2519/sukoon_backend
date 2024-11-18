import json
import dataclasses
from flask import request
from flask_restful import Resource
from shared.models.interfaces import BulkUploadInput
from models.bulk_insert_users.main import BulkInsertUsers


class BulkInsertUsersService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = BulkUploadInput(**input)
        output = BulkInsertUsers(input).process()
        output = dataclasses.asdict(output)

        return output
