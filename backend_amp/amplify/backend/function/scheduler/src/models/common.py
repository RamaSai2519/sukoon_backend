from bson import ObjectId
from db.users import get_user_collection
from models.interfaces import User, Expert
from db.experts import get_experts_collections


class Common:
    def __init__(self):
        self.users_cache = {}
        self.experts_cache = {}
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()

    @staticmethod
    def clean_dict(doc: dict, dataClass) -> dict:
        if doc:
            document_fields = set(dataClass.__annotations__.keys())
            doc = {k: v for k, v in doc.items() if k in document_fields}
        return doc

    def get_expert(self, expert_id: ObjectId) -> Expert:
        experts_cache = self.experts_cache
        if expert_id not in experts_cache:
            expert = self.experts_collection.find_one({'_id': expert_id})
            if expert:
                expert = Common.clean_dict(expert, Expert)
                expert = Expert(**expert)
            else:
                expert = None
            experts_cache[expert_id] = expert
        return experts_cache[expert_id]

    def get_user(self, user_id: ObjectId) -> User:
        users_cache = self.users_cache
        if user_id not in users_cache:
            user = self.users_collection.find_one({'_id': user_id})
            if user:
                user = Common.clean_dict(user, User)
                user = User(**user)
            else:
                user = None
            users_cache[user_id] = user
        return users_cache[user_id]
