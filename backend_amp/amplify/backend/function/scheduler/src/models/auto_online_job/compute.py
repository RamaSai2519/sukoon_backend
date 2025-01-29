from shared.db.experts import get_experts_collections, get_timings_collection
from shared.models.common import Common


class Compute:
    def __init__(self) -> None:
        self.collection = get_experts_collections()
        self.now_time = Common.get_current_ist_time()
        self.timings_collection = get_timings_collection()

    def job(self) -> list:
        pass

    def compute(self) -> list:
        today = self.now_time.strftime("%A")
        experts = self.collection.find({"day": today})
