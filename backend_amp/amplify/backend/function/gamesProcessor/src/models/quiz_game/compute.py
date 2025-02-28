from shared.db.users import get_user_collection, get_user_stats_collection
from shared.models.interfaces import QuizGameInput as Input, Output
from shared.db.games import get_quiz_questions_collections
from shared.models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.stats_collection = get_user_stats_collection()
        self.questions_collection = get_quiz_questions_collections()

    def _get_questions_for_a_user_at_a_level(self, last_question_shown_at_this_level):
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

    def _get_last_played_question_at_level(self) -> dict:
        query = {"_id": ObjectId(self.input.user_id)}
        user = self.users_collection.find_one(query)
        user_stats_id = user.get("userGameStats")
        last_question_shown_at_this_level = 0

        if not user_stats_id:

            quiz_game_stats = {
                str(self.input.level): {
                    "lastQuestionShownAtThisLevel": self.input.question_to_show
                }
            }

            result = self.stats_collection.insert_one(
                {"quizGameStats": quiz_game_stats})
            user_stats_id = result.inserted_id

            self.users_collection.update_one(
                {"_id": ObjectId(self.input.user_id)},
                {"$set": {"userGameStats": user_stats_id}},
            )

        else:
            user_stats = self.stats_collection.find_one(
                {"_id": ObjectId(user_stats_id)})
            quiz_game_stats = user_stats.get("quizGameStats")

            if not quiz_game_stats:
                quiz_game_stats = {
                    str(self.input.level): {
                        "lastQuestionShownAtThisLevel": self.input.question_to_show
                    }
                }
                self.stats_collection.insert_one(
                    {"quizGameStats": quiz_game_stats})

            else:
                level_stats = quiz_game_stats.get(str(self.input.level))
                if not level_stats:
                    quiz_game_stats[str(self.input.level)] = {
                        "lastQuestionShownAtThisLevel": self.input.question_to_show
                    }
                else:

                    last_question_shown_at_this_level = level_stats.get(
                        "lastQuestionShownAtThisLevel")
                    quiz_game_stats[str(
                        self.input.level)]["lastQuestionShownAtThisLevel"] = last_question_shown_at_this_level + self.input.question_to_show

                self.stats_collection.update_one(
                    {"_id": ObjectId(user_stats_id)},
                    {"$set": {"quizGameStats": quiz_game_stats}},
                )

        return last_question_shown_at_this_level

    def compute(self) -> Output:

        last_question_shown_at_this_level = self._get_last_played_question_at_level()
        quiz_questions = self._get_questions_for_a_user_at_a_level(
            last_question_shown_at_this_level)

        return Output(
            output_details={"quiz_questions": Common.jsonify(quiz_questions)},
            output_message="Successfully fetched quiz questions"
        )
