from shared.models.interfaces import GetQuizQuestionsInput as Input, Output
from shared.db.games import get_quiz_questions_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_quiz_questions_collection()

    def compute(self) -> Output:
        cursor = self.collection.find()
        if self.input.page and self.input.size:
            cursor = Common.paginate_cursor(cursor, int(
                self.input.page), int(self.input.size))

        total = self.collection.count_documents({})

        return Output(
            output_details={
                'total': total,
                'data': Common.jsonify(list(cursor))
            }
        )
