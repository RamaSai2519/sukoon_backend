from shared.models.interfaces import GetUsersInput as Input, Output
from shared.db.experts import get_vacations_collection
from shared.db.users import get_user_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.collection = get_vacations_collection()
        self.users_collection = get_user_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_value, self.input.filter_value
        )
        if self.input.filter_field == 'isDeleted':
            query = Common.get_filter_query(
                self.input.filter_value, self.input.filter_value, 'bool'
            )
        if self.input.filter_field == 'user':
            query = Common.get_filter_query(
                'name', self.input.filter_value
            )
            users = self.users_collection.distinct('_id', query)
            query['user'] = {'$in': users}

        total = self.collection.count_documents(query)
        if total <= 10:
            self.input.page = 1
            self.input.size = total
        cursor = self.collection.find(query)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size)
        )
        data = Common.jsonify(list(paginated_cursor))

        return Output(
            output_details={
                'data': data,
                'total': total
            },
            output_message="Successfully fetched vacation(s)"
        )
