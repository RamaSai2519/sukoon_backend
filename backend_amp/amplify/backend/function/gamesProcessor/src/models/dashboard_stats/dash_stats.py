from typing import Tuple
from models.common import Common
from helpers.experts import ExpertsHelper
from db.calls import get_calls_collection
from models.constants import successful_calls_query


class DashboardStats:
    def __init__(self, today_query: dict, exclude_query: dict, internal: str) -> None:
        self.common = Common()
        self.internal = internal
        self.today_query = today_query
        self.exclude_query = exclude_query
        self.experts_helper = ExpertsHelper()
        self.calls_collection = get_calls_collection()
        self.total_successful_calls, self.total_duration = self._total_successful_calls_and_duration_()

    def _total_successful_calls_and_duration_(self) -> Tuple[int, int]:
        query = {
            **self.exclude_query,
            **successful_calls_query, "duration": {"$exists": True}
        }
        projection = {"duration": 1, "_id": 0}
        successful_calls_data = self.common.get_calls(
            query, projection, False, False)

        total_seconds = [
            Common.duration_str_to_seconds(call["duration"])
            for call in successful_calls_data
            if Common.duration_str_to_seconds(call["duration"]) > 60
        ]

        return len(total_seconds), sum(total_seconds)

    def _get_successful_scheduled_calls_(self) -> list:
        query = {**successful_calls_query, **self.exclude_query,
                 "$or": [{"type": "scheduled"}, {"scheduledId": {"$exists": True}}]}
        projection = {"duration": 1, "scheduledId": 1, "type": 1, "_id": 0}
        calls = self.common.get_calls(query, projection, False)

        for call in calls:
            seconds = Common.duration_str_to_seconds(
                call["duration"]) if "duration" in call else 0
            if seconds < 60:
                calls.remove(call)
        return calls

    def _get_avg_conversation_score_(self) -> float:
        query = {
            **self.exclude_query,
            "conversationScore": {"$exists": True, "$gt": 0, "$ne": None}
        }
        projection = {"conversationScore": 1, "_id": 0}
        calls = self.common.get_calls(query, projection, False, False)
        scores = [call["conversationScore"] for call in calls]
        return round(sum(scores) / len(scores), 2) if scores else 0

    def total_calls(self) -> int:
        return self.calls_collection.count_documents(self.exclude_query)

    def today_calls(self) -> int:
        return self.calls_collection.count_documents({**self.today_query, **self.exclude_query})

    def successful_calls(self) -> int:
        return self.calls_collection.count_documents({**successful_calls_query, **self.exclude_query})

    def today_successful_calls(self) -> int:
        return self.calls_collection.count_documents({**successful_calls_query, **self.today_query, **self.exclude_query})

    def inadequate_calls(self) -> int:
        return self.calls_collection.count_documents({"status": "inadequate", **self.exclude_query})

    def today_inadequate_calls(self) -> int:
        return self.calls_collection.count_documents({"status": "inadequate", **self.today_query, **self.exclude_query})

    def failed_calls(self) -> int:
        return self.calls_collection.count_documents({"status": "failed", **self.exclude_query})

    def today_failed_calls(self) -> int:
        return self.calls_collection.count_documents({"status": "failed", **self.today_query, **self.exclude_query})

    def missed_calls(self) -> int:
        return self.calls_collection.count_documents({"status": "missed", **self.exclude_query})

    def today_missed_calls(self) -> int:
        return self.calls_collection.count_documents({"status": "missed", **self.today_query, **self.exclude_query})

    def average_call_duration(self) -> int:
        return Common.seconds_to_duration_str(
            self.total_duration / self.total_successful_calls
            if self.total_successful_calls > 0 else 0
        )

    def scheduled_calls_percentage(self) -> float:
        successful_scheduled_calls = len(
            self._get_successful_scheduled_calls_())
        return round(
            successful_scheduled_calls / self.total_successful_calls * 100
            if self.total_successful_calls > 0 else 0, 2
        )

    def avg_conversation_score(self) -> float:
        return self._get_avg_conversation_score_()

    def onlineSarathis(self) -> list:
        exclude_query = self.common.get_internal_exclude_query(
            self.internal, "_id")
        query = {"status": "online", **exclude_query}
        return self.experts_helper.get_experts(query)

    def _get_successful_scheduled_calls_(self) -> list:
        query = {**successful_calls_query, **self.exclude_query,
                 "$or": [{"type": "scheduled"}, {"scheduledId": {"$exists": True}}]}
        projection = {"duration": 1, "scheduledId": 1, "type": 1, "_id": 0}
        calls = self.common.get_calls(query, projection, False)

        for call in calls:
            seconds = Common.duration_str_to_seconds(
                call["duration"]) if "duration" in call else 0
            if seconds < 60:
                calls.remove(call)
        return calls
