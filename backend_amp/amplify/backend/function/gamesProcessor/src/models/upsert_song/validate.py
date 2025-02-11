from shared.models.interfaces import UpsertSongInput as Input
from bson import ObjectId


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

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

        return True, ''
