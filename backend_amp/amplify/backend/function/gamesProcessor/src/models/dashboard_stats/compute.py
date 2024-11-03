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
        self.today_query = Common.get_today_query()
        self.exclude_query = self.common.get_internal_exclude_query(input.internal)

    def get_dashboard_stats(self) -> Output:
        stats = DashboardStats(self.today_query, self.exclude_query, self.input.internal)
        stats_data = {}

        methods_to_run = [
            "avg_conversation_score", "onlineSarathis",
            "missed_calls", "today_missed_calls", "average_call_duration",
            "total_calls", "today_calls", "successful_calls", "today_successful_calls",
            "inadequate_calls", "today_inadequate_calls", "failed_calls", "today_failed_calls",
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
            output_message="Dashboard Stats",
            output_status=OutputStatus.SUCCESS
        )

    def _get_insights(self) -> dict:
        insights = CallInsights(self.exclude_query).get_insights()

        def create_row(key: str, category: str, value_name: str) -> dict:
            value = insights.get(value_name, "0")
            return {"key": key, "category": category, "value": value}

        successfulCalls = [
            create_row("1", "< 15 mins", "_15min"),
            create_row("2", "15-30 mins", "_15_30min"),
            create_row("3", "30-45 mins", "_30_45min"),
            create_row("4", "45-60 mins", "_45_60min"),
            create_row("5", "> 60 mins", "_60min_")
        ]
        avgCallDuration = [
            create_row("1", "First Call", "one_call"),
            create_row("2", "Second Call", "two_calls"),
            create_row("3", "Repeat Calls", "repeat_calls"),
            create_row("4", "Scheduled Calls", "scheduled_avg_duration"),
            create_row("5", "Organic Calls", "organic_avg_duration"),
        ]
        otherStats = [
            create_row("1", "First Call Split", "first_calls_split"),
            create_row("2", "Second Call Split", "second_calls_split"),
            create_row("3", "Repeat Call Split", "repeat_calls_split"),
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
