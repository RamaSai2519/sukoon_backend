import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.interfaces import ChatInput, Output
from models.get_chat.main import Chat


class ChatService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = ChatInput(**input)
        output = Chat(input).process()
        output = dataclasses.asdict(output)

        return output