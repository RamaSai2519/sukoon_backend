import json
from flask import request, Response
from shared.models.constants import OutputStatus
from shared.db.misc import get_display_messages_collection


class Handler:
    def __init__(self, response: Response) -> None:
        self.response = response
        self.messages_collection = get_display_messages_collection()

    def determine_message(self, route: str, method: str, status: str) -> str:
        query = {"route": route, "method": method, "status": status}
        message = self.messages_collection.find_one(query)
        if message:
            return message.get("message", None)
        return None

    def create_empty_message(self, route: str, method: str, status: str) -> None:
        query = {"route": route, "method": method, "status": status}
        self.messages_collection.update_one(
            query, {"$set": {"message": None}}, upsert=True
        )

    def handle_after_request(self) -> dict:
        output = self.response.get_json()
        if not output:
            return self.response
        route = request.path
        method = request.method
        if "output_status" in output:
            status = output["output_status"]
        else:
            status = OutputStatus.FAILURE

        message = self.determine_message(route, method, status)
        if message:
            output["display_message"] = message
        else:
            self.create_empty_message(route, method, status)
            output["display_message"] = output.get("output_message", "")
        self.response.data = json.dumps(output)
        if "output_status" in output and output["output_status"] == OutputStatus.FAILURE:
            self.response.status_code = 400
        return self.response
