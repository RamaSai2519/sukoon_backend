from shared.models.interfaces import GetHistoriesInput as Input, Output
from shared.db.chat import get_histories_collection
from shared.models.constants import OutputStatus
from shared.db.users import get_user_collection
from shared.models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_cache = {}
        self.common = Common()
        self.users_collection = get_user_collection()
        self.histories_collection = get_histories_collection()

    def get_user(self, phone_number: str) -> dict:
        if not self.users_cache.get(phone_number):
            query = {'phoneNumber': phone_number}
            self.users_cache[phone_number] = self.users_collection.find_one(
                query, {'name': 1})
        return self.users_cache[phone_number]

    def __format__(self, histories: list) -> list:
        for history in histories:
            user = self.get_user(history['phoneNumber'])
            history['user'] = user
            history = Common.jsonify(history)
        return histories

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)
        if self.input.filter_field == '_id':
            query['_id'] = ObjectId(self.input.filter_value)

        cursor = self.histories_collection.find(query).sort('updatedAt', -1)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size))
        histories = list(paginated_cursor)
        total_histories = self.histories_collection.count_documents(query)
        return Output(
            output_details={
                'data': self.__format__(histories),
                'total': total_histories
            },
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched expert(s)"
        )
