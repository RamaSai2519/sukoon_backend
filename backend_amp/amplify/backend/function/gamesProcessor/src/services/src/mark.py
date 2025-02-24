import json
import dataclasses
from flask import request
from flask_restful import Resource
from shared.models.common import Common
from models.get_prompts.main import GetPrompts
from models.upsert_prompt.main import UpsertPrompt
from models.get_histories.main import GetHistories
from models.delete_history.main import DeleteHistory
from models.get_beta_testers.main import GetBetaTesters
from models.upsert_beta_tester.main import UpsertBetaTester
from models.update_expert_scores.main import UpdateExpertScores
from shared.models.interfaces import UpdateScoresInput, UpsertPromptInput, GetPromptsInput, GetHistoriesInput, DeleteHistoryInput, UpsertBetaTesterInput, GetBetaTestersInput


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


class HistoriesService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetHistoriesInput(**input_params)
        output = GetHistories(input).process()
        output = dataclasses.asdict(output)

        return output

    def delete(self) -> dict:
        input_params = request.args
        input_params = Common.clean_dict(input_params, DeleteHistoryInput)
        input = DeleteHistoryInput(**input_params)
        output = DeleteHistory(input).process()
        output = dataclasses.asdict(output)

        return output


class BetaTesterService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertBetaTesterInput(**input)
        output = UpsertBetaTester(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetBetaTestersInput(**input_params)
        output = GetBetaTesters(input).process()
        output = dataclasses.asdict(output)

        return output
