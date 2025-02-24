from shared.models.interfaces import DeleteHistoryInput as Input, Output
from shared.db.chat import get_histories_collection
from shared.models.common import Common
from datetime import timedelta


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.histories_collection = get_histories_collection()

    def compute(self) -> tuple:
        new_date = Common.get_current_utc_time() - timedelta(days=1)
        new_date = new_date.strftime('%Y-%m-%d')

        query = {'phoneNumber': self.input.phoneNumber,
                 'context': self.input.context, 'createdAt': self.input.createdAt}
        self.histories_collection.update_one(
            query, {'$set': {'createdAt': new_date}})

        return Output(output_message='History deleted successfully')
