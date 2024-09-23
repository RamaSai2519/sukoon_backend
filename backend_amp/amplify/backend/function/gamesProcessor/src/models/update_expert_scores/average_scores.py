import requests
from configs import CONFIG as config
from db.calls import get_callsmeta_collection, get_calls_collection
from models.interfaces import UpdateScoresInput as Input, AverageScores, AverageScoresObject


class CalcAverageScores:
    def __init__(self, input: Input, callsmetas: list) -> None:
        self.input = input
        self.calls = callsmetas
        self.self_url = config.URL + "/actions/expert"
        self.main_field = "Conversation Score"
        self.calls_collection = get_calls_collection()
        self.callsmeta_collection = get_callsmeta_collection()
        self.score_fields = ["openingGreeting", "timeSplit", "userSentiment",
                             "flow", "timeSpent", "probability", "closingGreeting"]

    def get_all_calls_scores(self) -> dict:
        expert_scores = {}
        main_field = self.main_field
        for call in self.calls:
            score_breakup: dict = call.get("Score Breakup", {})

            if not score_breakup or isinstance(score_breakup, str):
                continue
            else:
                for field in self.score_fields:
                    score = score_breakup.get(field, 0)
                    if field not in expert_scores:
                        expert_scores[field] = []
                    expert_scores[field].append(score)

                score = call.get(main_field, 0)
                if main_field not in expert_scores:
                    expert_scores[main_field] = []
                expert_scores[main_field].append(score)
        print(expert_scores)
        return expert_scores

    def get_total_scores(self, expert_scores: dict) -> dict:
        total_scores = {}
        for field in self.score_fields:
            total_scores[field] = len(expert_scores[field])
        total_scores[self.main_field] = len(expert_scores[self.main_field])

        return total_scores

    def get_average_scores(self, expert_scores: dict, total_scores: dict) -> dict:
        average_scores = {}
        for field in self.score_fields + [self.main_field]:
            total_sum = sum(expert_scores[field])
            total = total_scores[field]
            average_scores[field] = round(total_sum / total, 2) if total != 0 else 0

        return average_scores

    def separate_main_field(self, average_scores: dict) -> tuple:
        score = average_scores.get(self.main_field, 0)
        average_scores = {
            key: value for key, value in average_scores.items() if key != self.main_field}
        average_scores = AverageScores(**average_scores)
        return score, average_scores

    def get_payload(self, average_scores: AverageScores, score: float) -> dict:
        return {"phoneNumber": self.input.expert_number,
                **average_scores.__dict__, "score": score}

    def update_expert_scores(self, average_scores: AverageScores, score: float) -> str:
        payload = self.get_payload(average_scores, score)
        headers = {'Content-Type': 'application/json'}
        response = requests.request(
            "POST", self.self_url, headers=headers, data=payload)
        if response.status_code != 200:
            message = f"Failed to update expert scores: {response.text}"
        message = "Successfully updated expert scores"
        return message

    def compute(self) -> dict:
        expert_scores = self.get_all_calls_scores()
        total_scores = self.get_total_scores(expert_scores)
        average_scores = self.get_average_scores(expert_scores, total_scores)
        score, average_scores = self.separate_main_field(average_scores)
        message = self.update_expert_scores(average_scores, score)

        return AverageScoresObject(**{
            "score": score,
            "message": message,
            "average_scores": average_scores,
        })
