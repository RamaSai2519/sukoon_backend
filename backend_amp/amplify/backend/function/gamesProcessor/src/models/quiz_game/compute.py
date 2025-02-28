from shared.db.users import get_user_collection, get_user_stats_collection
from shared.models.interfaces import QuizGameInput as Input, Output
from shared.db.games import get_quiz_questions_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.stats_collection = get_user_stats_collection()
        self.questions_collection = get_quiz_questions_collection()

    def _get_questions_for_a_user_at_a_level(self, last_question_shown_at_this_level=0):
        query = {"level": self.input.level}
        total_questions_at_this_level = self.questions_collection.count_documents(
            query)
        query = {"level": self.input.level, "category": self.input.category}
        project = {"question": 1, "category": 1, "options": 1, "_id": 0}
        if (last_question_shown_at_this_level + self.input.question_to_show) > total_questions_at_this_level:
            query["questionNumber"] = {"$gte": 1,
                                       "$lte": self.input.question_to_show}
            quiz_questions = self.questions_collection.find(
                query, project)
        else:
            query["questionNumber"] = {"$gt": last_question_shown_at_this_level,
                                       "$lte": last_question_shown_at_this_level + self.input.question_to_show}
            quiz_questions = self.questions_collection.find(query, project)

        return list(quiz_questions)

    def compute(self) -> Output:

        quiz_questions = self._get_questions_for_a_user_at_a_level()

        return Output(
            output_details={"quiz_questions": Common.jsonify(quiz_questions)},
            output_message="Successfully fetched quiz questions"
        )
