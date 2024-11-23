import json
import requests
from shared.configs import CONFIG as config
from shared.models.constants import OutputStatus
from shared.db.calls import get_callsmeta_collection
from shared.models.interfaces import UpdateScoresInput as Input, Output
from models.update_expert_scores.average_scores import CalcAverageScores, AverageScoresObject


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.self_url = config.URL + "/actions/expert"
        self.callsmeta_collection = get_callsmeta_collection()

    def get_expert_callsmeta(self) -> list:
        query = {"expert": self.input.expert_id}
        calls = self.callsmeta_collection.find(query)
        return list(calls)

    def set_users_per_expert(self, calls: list, expert_id: str) -> tuple:
        total_users_of_expert = set()
        user_calls_to_experts = {}

        for call in calls:
            user_id = str(call.get("user"))
            total_users_of_expert.add(user_id)

            if not user_calls_to_experts.get(user_id):
                user_calls_to_experts[user_id] = []

            user_calls_to_experts[user_id].append(call.get("callId"))

        return total_users_of_expert, user_calls_to_experts

    def calculate_repeat_ratio(self, expert_id: str, calls: list) -> float:
        total_users_of_expert, user_calls_to_experts = self.set_users_per_expert(
            calls, expert_id)

        repeat_users = 0
        total_users = len(total_users_of_expert)

        for user_id in user_calls_to_experts:
            if len(user_calls_to_experts[user_id]) > 2:
                repeat_users += 1

        repeat_ratio = (repeat_users / total_users) * \
            100 if total_users != 0 else 0
        repeat_ratio = round(repeat_ratio, 2)

        return repeat_ratio

    def calculate_normalized_calls(self, calls: list) -> float:
        total_calls = self.callsmeta_collection.count_documents({})
        normalized_calls = (len(calls) / total_calls) * \
            100 if total_calls != 0 else 0
        normalized_calls = round(normalized_calls, 2)

        return normalized_calls

    def calculate_expert_scores(self, calls: list, score) -> dict:
        expert_id = self.input.expert_id

        repeat_score = self.calculate_repeat_ratio(expert_id, calls)

        normalized_calls = self.calculate_normalized_calls(calls)

        final_score = ((score * 20) + repeat_score + normalized_calls) / 3
        final_score = round(final_score, 2)

        return {
            "total_score": final_score,
            "repeat_score": repeat_score,
            "calls_share": normalized_calls
        }

    def update_expert(self, final_scores: dict) -> str:
        payload = {"phoneNumber": self.input.expert_number, **final_scores}
        headers = {'Content-Type': 'application/json'}
        response = requests.request(
            "POST", self.self_url, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            message = f"Failed to update expert: {response.text}"
        message = "Successfully updated expert"
        return message

    def compute(self) -> Output:
        callsmetas = self.get_expert_callsmeta()
        calc_average_scores = CalcAverageScores(self.input, callsmetas)
        averages_object: AverageScoresObject = calc_average_scores.compute()
        final_scores = self.calculate_expert_scores(
            callsmetas, averages_object.score)
        message = self.update_expert(final_scores)

        return Output(
            output_details={**final_scores, **averages_object.__dict__},
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
