from shared.models.interfaces import GetHistoriesInput as Input, Output
from shared.db.chat import get_histories_collection
from shared.models.constants import OutputStatus
from shared.models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.histories_collection = get_histories_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)
        if self.input.filter_field == '_id':
            query['_id'] = ObjectId(self.input.filter_value)

        cursor = self.histories_collection.find(query).sort('_id', -1)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size))
        histories = list(paginated_cursor)
        total_histories = self.histories_collection.count_documents(query)
        return Output(
            output_details={
                'data': Common.jsonify(histories),
                'total': total_histories
            },
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched expert(s)"
        )
