from shared.models.interfaces import GetGamePlayInput, BytePlusTokenInput, UpdateGamePlayInput, CalculateWinnerInput, ScoreUpdaterInput, CardGameInput
from models.calculate_winner.main import CalculateWinner
from models.update_game_play.main import UpdateGamePlay
from models.byteplus_token.main import BytePlusToken
from models.score_updater.main import ScoreUpdater
from models.get_game_play.main import GetGamePlay
from models.card_game.main import CardGame
from flask_restful import Resource
from flask import request
import dataclasses
import json


class CardGameService(Resource):

    def post(self) -> None:
        input = json.loads(request.get_data())
        input = CardGameInput(**input)
        output = CardGame(input).process()
        output = dataclasses.asdict(output)

        return output


class ScoreUpdaterService(Resource):

    def post(self) -> None:
        input = json.loads(request.get_data())
        input = ScoreUpdaterInput(**input)
        output = ScoreUpdater(input).process()
        output = dataclasses.asdict(output)

        return output


class CalculateWinnerService(Resource):

    def post(self) -> None:
        input = json.loads(request.get_data())
        input = CalculateWinnerInput(**input)
        output = CalculateWinner(input).process()
        output = dataclasses.asdict(output)

        return output


class GameHistoryService(Resource):

    def post(self) -> None:
        input = json.loads(request.get_data())
        input = UpdateGamePlayInput(**input)
        output = UpdateGamePlay(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> None:
        input_params = request.args
        input = GetGamePlayInput(**input_params)
        output = GetGamePlay(input).process()
        output = dataclasses.asdict(output)

        return output


class BytePlusTokenService(Resource):

    def post(self) -> None:
        input = json.loads(request.get_data())
        input = BytePlusTokenInput(**input)
        output = BytePlusToken(input).process()
        output = dataclasses.asdict(output)

        return output
