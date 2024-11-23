from shared.db.whatsapp import get_whatsapp_templates_collection, get_whatsapp_temp_collection
from shared.models.constants import application_json_header
from shared.configs import CONFIG as config
from bson.objectid import ObjectId
from datetime import datetime
import requests
import json


class Helper:
    def __init__(self) -> None:
        self.waUrl = config.URL + "/actions/send_whatsapp"
        self.temp_collection = get_whatsapp_temp_collection()
        self.templates_collection = get_whatsapp_templates_collection()

    def format_input(self, inputs: dict) -> dict:
        output_dict = {}
        for key, value in inputs.items():
            new_key = key.replace('<', '').replace('>', '')
            output_dict[new_key] = value
        return output_dict

    def prepare_payload(self, user: dict, templateId: str, inputs: dict) -> dict:
        template = self.find_template(templateId)
        if template == "":
            return {}
        inputs = self.format_input(inputs)
        if "user_name" in inputs:
            inputs["user_name"] = user.get("name", "User")
        payload = {
            "phone_number": user.get("phoneNumber", ""),
            "template_name": template,
            "parameters": inputs
        }
        return payload

    def find_template(self, templateId: str) -> str:
        template = dict(self.templates_collection.find_one(
            {"_id": ObjectId(templateId)}))
        template = template.get("name", "")
        return template

    def send_whatsapp_message(self, payload: dict, messageId: str) -> requests.Response:
        headers = application_json_header
        response = requests.request(
            "POST", self.waUrl, headers=headers, data=json.dumps(payload))
        self.temp_collection.insert_one({
            "phoneNumber": payload.get("phone_number", ""),
            "responseCode": response.status_code,
            "responseText": response.text,
            "messageId": messageId,
            "datetime": datetime.now()
        })
        print(response.text)
        return response
