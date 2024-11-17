import json
import asyncio
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_club_interests.main import GetInterests
from models.invoice_generator.main import GenerateInvoice
from models.create_club_interest.main import CreateClubInterest
from models.interfaces import CreateClubInterestInput, GetClubInterestsInput, InvoiceData


class ClubService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetClubInterestsInput(**input_params)
        output = GetInterests(input).process()
        output = dataclasses.asdict(output)

        return output

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = CreateClubInterestInput(**input)
        output = CreateClubInterest(input).process()
        output = dataclasses.asdict(output)

        return output


class InvoiceService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = InvoiceData(**input)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output = loop.run_until_complete(GenerateInvoice(input).process())
        output = dataclasses.asdict(output)

        return output
