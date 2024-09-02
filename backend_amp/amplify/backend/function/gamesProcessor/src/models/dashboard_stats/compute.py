import pytz
from datetime import datetime
from models.common import Common
from models.constants import OutputStatus
from models.dashboard_stats.dash_stats import DashboardStats
from models.dashboard_stats.call_insights import CallInsights
from concurrent.futures import ThreadPoolExecutor, as_completed
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
