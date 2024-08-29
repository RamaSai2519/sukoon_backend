from models.common import Common
from models.constants import successful_calls_query
from concurrent.futures import ThreadPoolExecutor, as_completed


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
        scheduled_calls = self._get_successful_scheduled_calls_()
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
