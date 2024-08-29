import pytz
from typing import Tuple
from datetime import datetime
from models.common import Common
from helpers.experts import ExpertsHelper
from db.calls import get_calls_collection
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.constants import OutputStatus, successful_calls_query
from models.interfaces import DashboardStatsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.current_date = datetime.now(pytz.timezone("Asia/Kolkata"))

        # Today Query
        today_start = datetime.combine(self.current_date, datetime.min.time())
        today_end = datetime.combine(self.current_date, datetime.max.time())
        self.today_query = {"initiatedTime": {
            "$gte": today_start, "$lt": today_end}}

    def get_dashboard_stats(self) -> Output:
        stats = DashboardStats(self.today_query)
        stats_data = {}

        methods_to_run = [
            "total_calls", "today_calls", "successful_calls", "today_successful_calls",
            "failed_calls", "today_failed_calls", "missed_calls", "today_missed_calls",
            "average_call_duration", "scheduled_calls_percentage", "avg_conversation_score",
            "onlineSarathis"
        ]

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(getattr(stats, method)): method
                for method in methods_to_run
            }

            for future in as_completed(futures):
                method = futures[future]
                result = future.result()
                stats_data[method] = result

        stats_data["total_duration"] = self.common.seconds_to_duration_str(
            stats.total_duration
        )

        return Output(
            output_details=stats_data,
            output_status=OutputStatus.SUCCESS,
            output_message="Dashboard Stats"
        )

    def _get_insights(self):
        insights = CallInsights().get_insights()
        successfulCalls = [
            {"key": "1", "category": "< 15 mins",
                "value": insights.get("_15min", "0%")},
            {"key": "2", "category": "15-30 mins",
                "value": insights.get("_15_30min", "0%")},
            {"key": "3", "category": "30-45 mins",
                "value": insights.get("_30_45min", "0%")},
            {"key": "4", "category": "45-60 mins",
                "value": insights.get("_45_60min", "0%")},
            {"key": "5", "category": "> 60 mins",
                "value": insights.get("_60min_", "0%")},
        ]
        avgCallDuration = [
            {"key": "1", "category": "First Call",
                "value": insights.get("one_call", "0")},
            {"key": "2", "category": "Second Call",
                "value": insights.get("two_calls", "0")},
            {"key": "3", "category": "Repeat Calls",
                "value": insights.get("repeat_calls", "0")},
            {"key": "4", "category": "Scheduled Calls",
                "value": insights.get("scheduled_avg_duration", "0")},
            {"key": "5", "category": "Organic Calls",
                "value": insights.get("organic_avg_duration", "0")},
        ]
        otherStats = [
            {"key": "1", "category": "First Call Split",
                "value": insights.get("first_calls_split", "0%")},
            {"key": "2", "category": "Second Call Split",
                "value": insights.get("second_calls_split", "0%")},
            {"key": "3", "category": "Repeat Call Split",
                "value": insights.get("repeat_calls_split", "0%")},
        ]
        insights = {
            "successfulCalls": successfulCalls,
            "avgCallDuration": avgCallDuration,
            "otherStats": otherStats,
        }
        return insights

    def compute(self) -> Output:
        if self.input.item == "stats":
            return self.get_dashboard_stats()
        elif self.input.item == "insights":
            insights = self._get_insights()
            return Output(
                output_details=insights,
                output_status=OutputStatus.SUCCESS,
                output_message="Insights"
            )

        return Output(
            output_details={},
            output_status=OutputStatus.FAILURE,
            output_message="Invalid Item"
        )


class CallInsights:
    def __init__(self):
        self.common = Common()
        self.successful_calls = self._get_successful_calls()

    def _get_successful_calls(self) -> list:
        return self.common.get_calls(
            {"status": "successfull", "failedReason": ""},
            {"duration": 1, "user": 1, "type": 1, "_id": 0},
            False,
            False,
        )

    @staticmethod
    def _get_duration_category(duration_sec):
        if duration_sec < 900:
            return "_15min"
        elif 900 <= duration_sec < 1800:
            return "_15_30min"
        elif 1800 <= duration_sec < 2700:
            return "_30_45min"
        elif 2700 <= duration_sec < 3600:
            return "_45_60min"
        else:
            return "_60min_"

    def _classify_durations(self):
        duration_counts = {
            "_15min": 0,
            "_15_30min": 0,
            "_30_45min": 0,
            "_45_60min": 0,
            "_60min_": 0,
        }

        for call in self.successful_calls:
            duration_sec = self.common.duration_str_to_seconds(
                call["duration"])
            category = self._get_duration_category(duration_sec)
            duration_counts[category] += 1

        total_calls = len(self.successful_calls)
        for key in duration_counts:
            duration_counts[key] = str(
                round((duration_counts[key] / total_calls) * 100, 2)) + "%"

        return duration_counts

    def _get_calls_by_user(self):
        unique_users = set(call["user"] for call in self.successful_calls)
        calls_by_user = {user: [] for user in unique_users}
        for call in self.successful_calls:
            calls_by_user[call["user"]].append(call)
        return calls_by_user

    def _get_user_types(self, calls_by_user):
        user_types = {}
        for user, user_calls in calls_by_user.items():
            call_count = len(user_calls)
            if call_count == 1:
                user_type = "one_call"
            elif call_count == 2:
                user_type = "two_calls"
            else:
                user_type = "repeat_calls"
            user_types[user] = user_type
        return user_types

    def _calculate_average_durations(self, calls_by_user, user_types):
        durations_by_type = {}
        for user, user_calls in calls_by_user.items():
            user_type = user_types[user]
            if user_type not in durations_by_type:
                durations_by_type[user_type] = {"sum": 0, "count": 0}
            for call in user_calls:
                durations_by_type[user_type]["sum"] += self.common.duration_str_to_seconds(
                    call["duration"])
                durations_by_type[user_type]["count"] += 1

        return {
            user_type: self.common.seconds_to_duration_str(
                data["sum"] / data["count"])
            for user_type, data in durations_by_type.items()
        }

    @staticmethod
    def _calculate_split(calls_by_user: dict) -> dict:
        first_calls = len(
            [1 for user, calls in calls_by_user.items() if len(calls) == 1])
        second_calls = len(
            [1 for user, calls in calls_by_user.items() if len(calls) == 2])
        repeat_calls = len(
            [1 for user, calls in calls_by_user.items() if len(calls) > 2])

        total_calls = first_calls + second_calls + repeat_calls

        return {
            "first_calls_split": f"{round((first_calls / total_calls) * 100, 2)}%",
            "second_calls_split": f"{round((second_calls / total_calls) * 100, 2)}%",
            "repeat_calls_split": f"{round((repeat_calls / total_calls) * 100, 2)}%"
        }

    def _calculate_scheduled_avg_duration(self):
        scheduled_calls = Helper()._get_successful_scheduled_calls_()
        scheduled_call_durations = [
            self.common.duration_str_to_seconds(call["duration"]) for call in scheduled_calls
        ]
        return self.common.seconds_to_duration_str(
            sum(scheduled_call_durations) /
            len(scheduled_call_durations) if scheduled_call_durations else 0
        )

    def _calculate_organic_avg_duration(self):
        organic_calls = [
            call for call in self.successful_calls
            if "type" not in call or call["type"] != "scheduled"
        ]
        organic_call_durations = [
            self.common.duration_str_to_seconds(call["duration"]) for call in organic_calls
        ]
        return self.common.seconds_to_duration_str(
            sum(organic_call_durations) /
            len(organic_call_durations) if organic_call_durations else 0
        )

    def get_average_durations(self):
        calls_by_user = self._get_calls_by_user()
        user_types = self._get_user_types(calls_by_user)

        average_durations = self._calculate_average_durations(
            calls_by_user, user_types)
        split = self._calculate_split(calls_by_user)
        average_durations.update(split)

        average_durations["scheduled_avg_duration"] = self._calculate_scheduled_avg_duration(
        )
        average_durations["organic_avg_duration"] = self._calculate_organic_avg_duration(
        )

        return average_durations

    def get_insights(self):
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._classify_durations): 'durations',
                executor.submit(self.get_average_durations): 'averages'
            }

            insights_data = {}
            for future in as_completed(futures):
                insights_data.update(future.result())

        return insights_data


class DashboardStats:
    def __init__(self, today_query: dict) -> None:
        self.common = Common()
        self.today_query = today_query
        self.experts_helper = ExpertsHelper()
        self.calls_collection = get_calls_collection()
        self.total_successful_calls, self.total_duration = self._total_successful_calls_and_duration_()

    def _total_successful_calls_and_duration_(self) -> Tuple[int, int]:
        query = {**successful_calls_query, "duration": {"$exists": True}}
        projection = {"duration": 1, "_id": 0}
        successful_calls_data = self.common.get_calls(
            query, projection, False, False)

        total_seconds = [
            Common.duration_str_to_seconds(call["duration"])
            for call in successful_calls_data
            if Common.duration_str_to_seconds(call["duration"]) > 60
        ]

        return len(total_seconds), sum(total_seconds)

    def _get_avg_conversation_score_(self) -> float:
        query = {"Conversation Score": {
            "$exists": True, "$gt": 0, "$ne": None}}
        projection = {"Conversation Score": 1, "_id": 0}
        calls = self.common.get_calls(query, projection, False, False)
        scores = [call["Conversation Score"] for call in calls]
        return round(sum(scores) / len(scores), 2) if scores else 0

    def total_calls(self) -> int:
        return self.calls_collection.count_documents({})

    def today_calls(self) -> int:
        return self.calls_collection.count_documents(self.today_query)

    def successful_calls(self) -> int:
        return self.calls_collection.count_documents(successful_calls_query)

    def today_successful_calls(self) -> int:
        return self.calls_collection.count_documents({**successful_calls_query, **self.today_query})

    def failed_calls(self) -> int:
        return self.calls_collection.count_documents({"status": "failed"})

    def today_failed_calls(self) -> int:
        return self.calls_collection.count_documents({"status": "failed", **self.today_query})

    def missed_calls(self) -> int:
        return self.calls_collection.count_documents({"failedReason": "call missed"})

    def today_missed_calls(self) -> int:
        return self.calls_collection.count_documents({"failedReason": "call missed", **self.today_query})

    def average_call_duration(self) -> int:
        return Common.seconds_to_duration_str(
            self.total_duration / self.total_successful_calls
            if self.total_successful_calls > 0 else 0
        )

    def scheduled_calls_percentage(self) -> float:
        successful_scheduled_calls = len(
            Helper()._get_successful_scheduled_calls_())
        return round(
            successful_scheduled_calls / self.total_successful_calls * 100
            if self.total_successful_calls > 0 else 0, 2
        )

    def avg_conversation_score(self) -> float:
        return self._get_avg_conversation_score_()

    def onlineSarathis(self) -> list:
        query = {"status": "online"}
        return self.experts_helper.get_experts(query)


class Helper:
    def __init__(self) -> None:
        self.common = Common()

    def _get_successful_scheduled_calls_(self) -> list:
        query = {**successful_calls_query,
                 "$or": [{"type": "scheduled"}, {"scheduledId": {"$exists": True}}]}
        projection = {"duration": 1, "scheduledId": 1, "type": 1, "_id": 0}
        calls = self.common.get_calls(query, projection, False)

        for call in calls:
            seconds = Common.duration_str_to_seconds(
                call["duration"]) if "duration" in call else 0
            if seconds < 60:
                calls.remove(call)
        return calls
