from shared.models.interfaces import QuizGameInput, SaveGamePlayInput, GetLeaderBoardInput, GetQuizQuestionsInput, UpsertQuizQuestionInput
from models.upsert_quiz_question.main import UpsertQuizQuestion
from models.get_quiz_questions.main import GetQuizQuestions
from models.get_leaderboard.main import GetLeaderBoard
from models.save_game_play.main import SaveGamePlay
from models.quiz_game.main import QuizGame
from flask_restful import Resource
from flask import request
import dataclasses
import json


class QuizGameService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = QuizGameInput(**input)
        output = QuizGame(input).process()
        output = dataclasses.asdict(output)

        return output


class SaveGamePlayService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = SaveGamePlayInput(**input)
        output = SaveGamePlay(input).process()
        output = dataclasses.asdict(output)

        return output


class LeaderBoardService(Resource):

    def get(self) -> dict:
        input = request.args
        input = GetLeaderBoardInput(**input)
        output = GetLeaderBoard(input).process()
        output = dataclasses.asdict(output)

        return output


class QuizQuestionsService(Resource):

    def get(self) -> dict:
        input = request.args
        input = GetQuizQuestionsInput(**input)
        output = GetQuizQuestions(input).process()
        output = dataclasses.asdict(output)

        return output

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertQuizQuestionInput(**input)
        output = UpsertQuizQuestion(input).process()
        output = dataclasses.asdict(output)

        return output
