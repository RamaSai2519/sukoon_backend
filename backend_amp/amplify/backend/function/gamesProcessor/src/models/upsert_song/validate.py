from shared.db.users import get_admins_collection, get_user_collection
from shared.models.interfaces import UpsertSongInput as Input
from shared.db.experts import get_experts_collections
from bson import ObjectId


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.admins_collection = get_admins_collection()
        self.experts_collection = get_experts_collections()

    def validate_input(self) -> tuple:
        if not self.input.audio_url.startswith('https://') or not self.input.audio_url.endswith('.mp3'):
            return False, 'audio_url must be a valid mp3 url'

        if self.input.user_type not in ['user', 'expert', 'admin']:
            return False, 'user_type must be one of user, expert, admin'

        if self.input._id:
            try:
                ObjectId(self.input._id)
            except:
                return False, '_id must be a valid ObjectId'

        try:
            ObjectId(self.input.user_id)
        except:
            return False, 'user_id must be a valid ObjectId'

        if self.input.user_type == 'user':
            query = {'_id': ObjectId(self.input.user_id)}
            user = self.users_collection.find_one(query)
            if not user:
                return False, 'user_id does not exist'
        elif self.input.user_type == 'expert':
            query = {'_id': ObjectId(self.input.user_id)}
            expert = self.experts_collection.find_one(query)
            if not expert:
                return False, 'expert_id does not exist'
        else:
            query = {'_id': ObjectId(self.input.user_id)}
            admin = self.admins_collection.find_one(query)
            if not admin:
                return False, 'admin_id does not exist'

        return True, ''
