from shared.models.interfaces import RecordSongLikeInput as Input
from shared.db.content import get_songs_collection
from shared.db.users import get_user_collection
from bson import ObjectId


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.songs_collection = get_songs_collection()

    def _is_valid_user(self):
        query = {"_id": ObjectId(self.input.user_id)}
        user = self.users_collection.find_one(query)
        return user is not None

    def _is_valid_song(self):
        query = {"_id": ObjectId(self.input.item_id)}
        if self.input.item_type == "song":
            song = self.songs_collection.find_one(query)
            return song is not None
        return False

    def validate_input(self):
        if not self._is_valid_user():
            return False, "User not found"

        if not self._is_valid_song():
            return False, "Song not found"

        return True, ""
