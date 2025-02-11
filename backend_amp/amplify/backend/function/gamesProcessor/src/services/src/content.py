import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_chat.main import Chat
from models.get_photos.main import Photos
from models.get_songs.main import GetSongs
from models.upsert_song.main import UpsertSong
from models.save_content.main import SaveContent
from models.get_blogposts.main import GetBlogPosts
from models.generate_image.main import GenerateImage
from models.upsert_blogposts.main import UpsertBlogPost
from models.get_content_posts.main import GetContentPosts
from shared.models.interfaces import ChatInput, SaveContentInput, PhotosInput, Content, ContentPhoto, GetContentPostsInput, GetBlogPostsInput, BlogPostInput, UpsertSongInput, GetSongsInput


class ChatService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = ChatInput(**input)
        output = Chat(input).process()
        output = dataclasses.asdict(output)

        return output


class PhotoService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = PhotosInput(**input_params)
        output = Photos(input).process()
        output = dataclasses.asdict(output)

        return output


class ContentService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())

        input["content"] = Content(**input.get("content", {}))
        input["photo"] = ContentPhoto(**input.get("photo", {}))
        input = SaveContentInput(**input)
        output = SaveContent(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetContentPostsInput(**input_params)
        output = GetContentPosts(input).process()
        output = dataclasses.asdict(output)

        return output


class DallImageService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = ChatInput(**input_params)
        output = GenerateImage(input).process()
        output = dataclasses.asdict(output)

        return output


class BlogPostService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = BlogPostInput(**input)
        output = UpsertBlogPost(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetBlogPostsInput(**input_params)
        output = GetBlogPosts(input).process()
        output = dataclasses.asdict(output)

        return output


class SongService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertSongInput(**input)
        output = UpsertSong(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetSongsInput(**input_params)
        output = GetSongs(input).process()
        output = dataclasses.asdict(output)

        return output
