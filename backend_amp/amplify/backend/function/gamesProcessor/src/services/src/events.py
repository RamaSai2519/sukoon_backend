import json
from flask import request
from flask_restful import Resource


class UpdateEventsService(Resource):

    def post(self):
        input = json.loads(request.get_data())
        pass
