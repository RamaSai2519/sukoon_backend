import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_chat.main import Chat
from models.get_photos.main import Photos
from models.interfaces import ChatInput,  PhotosInput, Output


class ChatService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = ChatInput(**input)
        output = Chat(input).process()
        output = dataclasses.asdict(output)

        return output


class PhotosService(Resource):

    def get(self) -> Output:
        input_params = request.args
        input = PhotosInput(**input_params)
        output = Photos(input).process()
        output = dataclasses.asdict(output)

        return output
