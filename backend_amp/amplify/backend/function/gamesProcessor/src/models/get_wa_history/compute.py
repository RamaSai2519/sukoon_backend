from bson import ObjectId
from pprint import pprint
from shared.models.common import Common
from pymongo.collection import Collection
from shared.models.constants import OutputStatus
from shared.db.calls import get_calls_collection
from shared.db.experts import get_experts_collections
from shared.models.interfaces import GetWaHistoryInput as Input, Output
from shared.db.users import get_user_webhook_messages_collection, get_user_whatsapp_feedback_collection, get_user_collection, get_meta_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.cache = {}
        self.input = input
        self.common = Common()
        self.meta_collection = get_meta_collection()
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()
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

    def get_metadata(self, user_id: ObjectId) -> str:
        if user_id not in self.cache:
            cache_doc = {}
            query = {'user': user_id}
            doc = self.meta_collection.find_one(query)
            if doc:
                cache_doc['user_status'] = doc.get('userStatus')

            internal_query = self.common.get_internal_exclude_query()
            query = {**query, **internal_query}
            query['status'] = 'successful'
            calls = self.calls_collection.count_documents(query)
            cache_doc['fc_done'] = 'Yes' if calls >= 1 else 'No'

            internal_query = self.common.get_internal_exclude_query('true')
            query = {**query, **internal_query}
            calls = self.calls_collection.find(
                query).sort('initiatedTime', -1).limit(1)
            calls = list(calls)
            if len(calls) > 0:
                cache_doc['last_in_call'] = calls[0].get('status')
            else:
                cache_doc['last_in_call'] = 'Not Done'

            self.cache[user_id] = cache_doc
        return self.cache[user_id]

    def format_messages(self, documents: list) -> list:
        for document in documents:
            if document.get("userId"):
                document = self.populate_user_details(document)
                metadata = self.get_metadata(ObjectId(document["userId"]))
                document.update(metadata)
        return documents

    def format_feedbacks(self, documents: list) -> list:
        for document in documents:
            document["userName"] = self.common.get_user_name(
                ObjectId(document.get("userId")))
            document["expertName"] = self.common.get_expert_name(
                ObjectId(document.get("sarathiId")))
            document["body"] = document["body"][2:].replace("_", " ")
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
                "total": total,
                "page": int(self.input.page),
                "pageSize": int(self.input.size),
                "data": Common.jsonify(documents),
            },
            output_message="Successfully fetched documents"
        )
