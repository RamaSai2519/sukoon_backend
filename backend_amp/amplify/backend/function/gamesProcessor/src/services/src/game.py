import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import QuizGameInput, Output
from models.quiz_game.main import QuizGame

from models.interfaces import CardGameInput, Output
from models.card_game.main import CardGame

from models.interfaces import ScoreUpdaterInput, Output
from models.score_updater.main import ScoreUpdater

from models.interfaces import CalculateWinnerInput, Output
from models.calculate_winner.main import CalculateWinner

from models.interfaces import UpdateGamePlayInput, Output
from models.update_game_play.main import UpdateGamePlay

from models.interfaces import GetGamePlayInput, Output
from models.get_game_play.main import GetGamePlay

from models.interfaces import BytePlusTokenInput, Output
from models.byteplus_token.main import BytePlusToken

class QuizGameService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = QuizGameInput(**input)
        output = QuizGame(input).process()
        output = dataclasses.asdict(output)

        return output
    

class CardGameService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = CardGameInput(**input)
        output = CardGame(input).process()
        output = dataclasses.asdict(output)

        return output
    

class ScoreUpdaterService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = ScoreUpdaterInput(**input)
        output = ScoreUpdater(input).process()
        output = dataclasses.asdict(output)

        return output
    
class CalculateWinnerService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = CalculateWinnerInput(**input)
        output = CalculateWinner(input).process()
        output = dataclasses.asdict(output)

        return output
    

class GameHistoryService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = UpdateGamePlayInput(**input)
        output = UpdateGamePlay(input).process()
        output = dataclasses.asdict(output)

        return output
    

    def get(self) -> Output:
        input_params = request.args
        input = GetGamePlayInput(**input_params)
        output = GetGamePlay(input).process()
        output = dataclasses.asdict(output)

        return output
    


class BytePlusTokenService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = BytePlusTokenInput(**input)
        output = BytePlusToken(input).process()
        output = dataclasses.asdict(output)

        return output
    
    
    

