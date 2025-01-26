from shared.models.common import Common
from shared.db.users import get_user_payment_collection
from shared.models.interfaces import GetPaymentsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_user_payment_collection()

    def compute(self) -> dict:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value
        )
        if self.input.filter_field in ['order_amount']:
            query = Common.get_filter_query(
                self.input.filter_field, self.input.filter_value, 'int'
            )

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
            output_message="Fetched Docs"
        )
