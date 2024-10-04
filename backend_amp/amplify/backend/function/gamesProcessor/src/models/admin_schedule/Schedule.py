from datetime import datetime, timedelta
from models.common import Common
from bson import ObjectId


class Schedule:
    def __init__(self, expert_id, user_id, time, duration=30, type="User"):
        self.expert_id = expert_id
        self.user_id = user_id
        self.time = time
        self.duration = duration
        self.type = type
        self.ist_offset = timedelta(hours=5, minutes=30)
        self.admin_id = self.get_admin_id()
        self.ist_time = self.convert_to_ist()

    def get_admin_id(self) -> ObjectId:
        try:
            return ObjectId(Common.get_identity())
        except Exception:
            return ObjectId("665b5b5310b36290eaa59d27")

    def convert_to_ist(self) -> datetime:
        date_object = datetime.strptime(self.time, "%Y-%m-%dT%H:%M:%S.%fZ")
        return date_object + self.ist_offset

    def to_document(self) -> dict:
        return {
            "expert": ObjectId(self.expert_id),
            "user": ObjectId(self.user_id),
            "lastModifiedBy": self.admin_id,
            "type": self.type,
            "datetime": self.ist_time,
            "status": "pending",
            "duration": int(self.duration),
        }
