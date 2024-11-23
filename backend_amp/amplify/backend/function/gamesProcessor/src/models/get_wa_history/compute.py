from bson import ObjectId
from shared.models.common import Common
from pymongo.collection import Collection
from shared.models.constants import OutputStatus
from shared.db.experts import get_experts_collections
from shared.models.interfaces import GetWaHistoryInput as Input, Output
from shared.db.users import get_user_webhook_messages_collection, get_user_whatsapp_feedback_collection, get_user_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()
        self.wafeedback_collection = get_user_whatsapp_feedback_collection()
        self.userwebhookmessages_collection = get_user_webhook_messages_collection()

    def fetch_documents(self, collection: Collection, query: dict) -> list:
        cursor = collection.find(query).sort("createdAt", -1)
        return list(Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size)))

    def populate_user_details(self, document: dict) -> dict:
        user = self.users_collection.find_one(
            {"_id": ObjectId(document["userId"])})
        if user:
            document["userName"] = user.get("name", "")
            document["userNumber"] = user.get("phoneNumber", "")
        else:
            document["userName"] = ""
            document["userNumber"] = ""
        return document

    def format_messages(self, documents: list) -> list:
        for document in documents:
            if document.get("userId"):
                document = self.populate_user_details(document)
            document = Common.jsonify(document)
        return documents

    def format_feedbacks(self, documents: list) -> list:
        for document in documents:
            document["userName"] = self.common.get_user_name(
                ObjectId(document.get("userId")))
            document["expertName"] = self.common.get_expert_name(
                ObjectId(document.get("sarathiId")))
            document["body"] = document["body"][2:].replace("_", " ")
            document = Common.jsonify(document)
        return documents

    def compute(self) -> Output:
        if self.input.type == "webhook":
            query = {"body": {"$ne": None}}
            collection = self.userwebhookmessages_collection
            documents = self.fetch_documents(collection, query)
            documents = self.format_messages(documents)
        elif self.input.type == "feedback":
            query = {}
            collection = self.wafeedback_collection
            documents = self.fetch_documents(collection, query)
            documents = self.format_feedbacks(documents)

        total = collection.count_documents(query)

        return Output(
            output_details={
                "data": documents,
                "total": total,
                "page": int(self.input.page),
                "pageSize": int(self.input.size)
            },
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched documents"
        )
