from models.interfaces import QuizGameInput as Input, Output
from models.constants import OutputStatus
from bson import ObjectId
from db.games import get_quiz_questions_collections 
from db.users import get_user_collection, get_user_stats_collection

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input


    def _remove_nested_ids(self, data):
        for item in data:
            for option in item.get('options', []):
                if '_id' in option:
                    del option['_id']
        return data


    def _get_questions_for_a_user_at_a_level(self, last_question_shown_at_this_level):

        quiz_questions_collection = get_quiz_questions_collections()

        total_questions_at_this_level = quiz_questions_collection.count_documents({"level": self.input.level})
        if last_question_shown_at_this_level + self.input.question_to_show > total_questions_at_this_level:
            quiz_questions = list(quiz_questions_collection.find({"level": self.input.level, "questionNumber": { "$gte": 1, "$lte": self.input.question_to_show } }, {"question": 1, "options":1, "_id": 0}))
        else:
            quiz_questions = list(quiz_questions_collection.find({"level": self.input.level, 
                        "questionNumber": { "$gt": last_question_shown_at_this_level, "$lte": last_question_shown_at_this_level + self.input.question_to_show } }, {"question": 1, "options":1, "_id": 0}))

        return quiz_questions


    def _get_last_played_question_at_level(self) -> dict:
        user_collection = get_user_collection()
        user = user_collection.find_one({"_id": ObjectId(self.input.user_id)})
        user_stats_id = user.get("userGameStats")
        user_stats_collection = get_user_stats_collection()
        last_question_shown_at_this_level = 0


        if not user_stats_id:

            quiz_game_stats = {
                str(self.input.level) : {
                    "lastQuestionShownAtThisLevel" : self.input.question_to_show
                }
            }

            result = user_stats_collection.insert_one({"quizGameStats": quiz_game_stats})
            user_stats_id = result.inserted_id

            user_collection.update_one(
                {"_id": ObjectId(self.input.user_id)},
                {"$set": {"userGameStats": user_stats_id}},
            )

        else:
            user_stats = user_stats_collection.find_one({"_id": ObjectId(user_stats_id)})
            quiz_game_stats = user_stats.get("quizGameStats")

            if not quiz_game_stats:
                quiz_game_stats = {
                    str(self.input.level) : {
                        "lastQuestionShownAtThisLevel" : self.input.question_to_show
                    }
                }
                user_stats_collection.insert_one({"quizGameStats": quiz_game_stats})

            else:
                level_stats = quiz_game_stats.get(str(self.input.level))
                if not level_stats:
                    quiz_game_stats[str(self.input.level)] = {
                        "lastQuestionShownAtThisLevel" : self.input.question_to_show
                    }
                else:

                    last_question_shown_at_this_level = level_stats.get("lastQuestionShownAtThisLevel")
                    quiz_game_stats[str(self.input.level)]["lastQuestionShownAtThisLevel"] = last_question_shown_at_this_level +  self.input.question_to_show

                user_stats_collection.update_one(
                    {"_id": ObjectId(user_stats_id)},
                    {"$set": {"quizGameStats": quiz_game_stats}},
                )

        return last_question_shown_at_this_level

    def compute(self):
        
        last_question_shown_at_this_level = self._get_last_played_question_at_level()
        quiz_questions = self._get_questions_for_a_user_at_a_level(last_question_shown_at_this_level)
        quiz_questions = self._remove_nested_ids(quiz_questions)

        print(quiz_questions)

        return Output(
            output_details= {"quiz_questions": quiz_questions},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )