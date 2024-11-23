import json
import dataclasses
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models.dashboard_stats.main import DashboardStats
from shared.models.interfaces import DashboardStatsInput, Output


class DashboardStatsService(Resource):

    @jwt_required()
    def get(self) -> Output:
        input_params = request.args
        input = DashboardStatsInput(**input_params)
        output = DashboardStats(input).process()
        output = dataclasses.asdict(output)

        return output
