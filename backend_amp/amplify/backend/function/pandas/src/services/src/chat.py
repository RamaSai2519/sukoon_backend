import json
import dataclasses
from flask import request
from models.chat.main import Chat
from flask_restful import Resource
from shared.models.interfaces import ChatInput


class ChatService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        print(input, "input")
        input = ChatInput(**input)
        output = Chat(input).process()
        output = dataclasses.asdict(output)

        return output
