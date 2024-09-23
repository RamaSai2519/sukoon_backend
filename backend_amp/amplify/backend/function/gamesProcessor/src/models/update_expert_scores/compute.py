import requests
from configs import CONFIG as config
from models.constants import OutputStatus
from db.calls import get_callsmeta_collection
from models.interfaces import UpdateScoresInput as Input, Output
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
        total_users_per_expert = {}
        user_calls_to_experts = {}

        for call in calls:
            user_id = str(call["user"])
            if expert_id not in total_users_per_expert:
                total_users_per_expert[expert_id] = set()
            if user_id not in user_calls_to_experts:
                user_calls_to_experts[user_id] = set()

            set(total_users_per_expert[expert_id]).add(user_id)
            set(user_calls_to_experts[user_id]).add(expert_id)

        return total_users_per_expert, user_calls_to_experts

    def calculate_repeat_ratio(self, expert_id: str, calls: list) -> float:
        repeat_users = 0
        total_users_per_expert, user_calls_to_experts = self.set_users_per_expert(
            calls, expert_id)
        total_users = len(total_users_per_expert.get(expert_id, []))
        for user_id in total_users_per_expert[expert_id]:
            if len(user_calls_to_experts.get(user_id, [])) > 1 and expert_id in user_calls_to_experts.get(user_id, []):
                repeat_users += 1
        repeat_ratio = (repeat_users / total_users) * \
            100 if total_users != 0 else 0

        return repeat_ratio

    def calculate_normalized_calls(self, calls: list) -> float:
        total_calls = self.callsmeta_collection.count_documents({})
        normalized_calls = (len(calls) / total_calls) * \
            100 if total_calls != 0 else 0
        normalized_calls = round(normalized_calls, 2)

        return normalized_calls

    def calculate_expert_scores(self, calls: list, score):
        expert_id = self.input.expert_id

        repeat_score = self.calculate_repeat_ratio(expert_id, calls)

        normalized_calls = self.calculate_normalized_calls(calls)

        final_score = int((score + repeat_score + normalized_calls) / 3)

        return {
            "total_score": final_score,
            "repeat_score": repeat_score,
            "calls_share": normalized_calls
        }

    def update_expert(self, final_scores: dict) -> str:
        payload = {"phoneNumber": self.input.expert_number, **final_scores}
        headers = {'Content-Type': 'application/json'}
        response = requests.request(
            "POST", self.self_url, headers=headers, data=payload)
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
        message = message + " and " + averages_object.message

        return Output(
            output_details=final_scores,
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
