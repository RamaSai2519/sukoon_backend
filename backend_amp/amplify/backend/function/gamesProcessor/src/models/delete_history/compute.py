from shared.models.interfaces import DeleteHistoryInput as Input, Output
from shared.db.chat import get_histories_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.histories_collection = get_histories_collection()

    def compute(self) -> tuple:
        now_date = Common.get_current_utc_time()
        now_date = now_date.strftime('%Y-%m-%d')

        query = {'phoneNumber': self.input.phoneNumber,
                 'context': self.input.context, 'createdAt': now_date}
        self.histories_collection.delete_one(query)

        return Output(output_message='History deleted successfully')
