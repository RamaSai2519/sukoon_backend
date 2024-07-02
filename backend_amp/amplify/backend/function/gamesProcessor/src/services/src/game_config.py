import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import GetGameConfigInput, UpdateGameConfigInput, Output
from models.get_game_config.main import GetGameConfig
from models.update_game_config.main import UpdateGameConfig


class GameConfigService(Resource):
    def get(self) -> Output:
        input_params = request.args
        input = GetGameConfigInput(**input_params)
        output = GetGameConfig(input).process()
        output = dataclasses.asdict(output)

        return output
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = UpdateGameConfigInput(**input)
        output = UpdateGameConfig(input).process()
        output = dataclasses.asdict(output)

        return output
    


