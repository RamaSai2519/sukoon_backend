from shared.models.interfaces import UpsertQuizQuestionInput as Input, Output
from shared.db.games import get_quiz_questions_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_quiz_questions_collection()

    def prep_data(self) -> dict:
        data = self.input.__dict__
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()
        return data

    def compute(self) -> Output:
        data = self.prep_data()
        option_fields = ['option1', 'option2', 'option3', 'option4']
        options = []
        for field, value in data.items():
            if field in option_fields:
                doc = {
                    'key': field,
                    'value': value,
                    'isCorrect': value == data['correctAnswer']
                }
                options.append(doc)

        doc = {
            'options': options,
            'level': data['level'],
            'question': data['question'],
            'category': data['category'],
            'imageUrl': data['imageUrl']
        }

        query = {'question': data['question']}
        doc = self.collection.find_one_and_update(
            query,
            {'$set': doc},
            upsert=True,
            return_document=True
        )

        return Output(
            output_details=Common.jsonify(doc),
            output_message='Quiz question upserted successfully'
        )
