from shared.models.common import Common
from shared.models.constants import user_balance_types
from shared.db.users import get_subscription_plans_collection
from shared.models.interfaces import GetSubPlansInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_subscription_plans_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)
        int_fields = user_balance_types + ["price"]
        if self.input.filter_field in int_fields:
            query = Common.get_filter_query(
                self.input.filter_field, self.input.filter_value, 'int')

        total = self.collection.count_documents(query)
        if total <= 10:
            self.input.page = 1
            self.input.size = total
        cursor = self.collection.find(query)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size))
        data = [Common.jsonify(d) for d in list(paginated_cursor)]

        return Output(
            output_details={
                "data": data,
                "total": total
            },
            output_message="Successfully fetched plan(s)"
        )
