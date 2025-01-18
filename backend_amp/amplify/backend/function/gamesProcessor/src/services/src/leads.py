import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_leads.main import GetLeads
from models.get_leads_count.main import GetLeadsCounts
from shared.models.interfaces import GetLeadsInput, GetLeadsCountInput


class LeadsService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetLeadsInput(**input_params)
        output = GetLeads(input).process()
        output = dataclasses.asdict(output)

        return output

class LeadsCountService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetLeadsCountInput(**input_params)
        output = GetLeadsCounts(input).process()
        output = dataclasses.asdict(output)

        return output