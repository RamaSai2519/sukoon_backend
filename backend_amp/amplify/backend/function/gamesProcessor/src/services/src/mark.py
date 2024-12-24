import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_prompts.main import GetPrompts
from models.upsert_prompt.main import UpsertPrompt
from models.update_expert_scores.main import UpdateExpertScores
from shared.models.interfaces import UpdateScoresInput, UpsertPromptInput, GetPromptsInput


class UpdateExpertScoresService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpdateScoresInput(**input)
        output = UpdateExpertScores(input).process()
        output = dataclasses.asdict(output)

        return output


class SystemPromptsService(Resource):

    def get(self) -> dict:
        input = GetPromptsInput()
        output = GetPrompts(input).process()
        output = dataclasses.asdict(output)

        return output

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertPromptInput(**input)
        output = UpsertPrompt(input).process()
        output = dataclasses.asdict(output)

        return output
