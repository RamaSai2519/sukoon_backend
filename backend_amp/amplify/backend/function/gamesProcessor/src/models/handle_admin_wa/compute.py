import threading
from bson import ObjectId
from shared.db.users import get_user_collection
from pymongo.collection import Collection
from shared.models.constants import OutputStatus
from models.handle_admin_wa.helper import Helper
from shared.models.interfaces import AdminWaInput as Input, Output
from shared.db.events import get_event_users_collection, get_events_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.helper = Helper()
        self.users_collection = get_user_collection()
        self.events_collection = get_events_collection()
        self.event_users_collection = get_event_users_collection()

    def create_users_query(self) -> dict:
        query = {"wa_opt_out": False}
        if self.input.usersType and self.input.usersType != "all":
            query["profileCompleted"] = self.input.usersType == "full"
        elif self.input.cities:
            query["city"] = {"$in": self.input.cities}
        else:
            return query
        return query

    def get_event_or_users_query(self) -> tuple:
        if self.input.eventId and self.input.usersType == "event":
            query = {"_id": ObjectId(self.input.eventId)}
            event = self.events_collection.find_one(query)
            return {"source": event["slug"]}, self.event_users_collection
        else:
            return self.create_users_query(), self.users_collection

    def get_users_count(self, query: dict, collection: Collection) -> int:
        return collection.count_documents(query)

    def get_users(self, query: dict, collection: Collection) -> list:
        return list(collection.find(query))

    def determine_users(self) -> list:
        query, collection = self.get_event_or_users_query()
        return self.get_users(query, collection)

    def final_send(self) -> None:
        users = self.determine_users()
        for user in users:
            inputs = self.input.inputs
            templateId = self.input.templateId
            payload = self.helper.prepare_payload(user, templateId, inputs)
            self.helper.send_whatsapp_message(payload, self.input.messageId)

    def get_preview(self) -> Output:
        query, collection = self.get_event_or_users_query()
        return self.get_users_count(query, collection)

    def compute(self) -> Output:
        if self.input.action == "preview":
            return Output(
                output_details={"usersCount": self.get_preview()},
                output_status=OutputStatus.SUCCESS,
                output_message="Preview generated successfully"
            )
        elif self.input.action == "send":
            threading.Thread(target=self.final_send).start()
            return Output(
                output_details={},
                output_status=OutputStatus.SUCCESS,
                output_message="Messages sent successfully"
            )
