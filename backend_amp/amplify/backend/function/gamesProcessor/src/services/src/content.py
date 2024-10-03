import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_chat.main import Chat
from models.get_photos.main import Photos
from models.save_content.main import SaveContent
from models.get_content_posts.main import GetContentPosts
from models.interfaces import ChatInput, SaveContentInput, PhotosInput, Output, Content, ContentPhoto, GetContentPostsInput


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


class ContentService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        
        input["content"] = Content(**input.get("content", {}))
        input["photo"] = ContentPhoto(**input.get("photo", {}))
        input = SaveContentInput(**input)
        output = SaveContent(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> Output:
        input_params = request.args
        input = GetContentPostsInput(**input_params)
        output = GetContentPosts(input).process()
        output = dataclasses.asdict(output)

        return output

    
