from shared.models.interfaces import GetRefTokenInput as Input, Output
from shared.db.referral import get_ref_tokens_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.ref_tokens_collection = get_ref_tokens_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value
        )

        cursor = self.ref_tokens_collection.find(query)

        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size)
        )

        data = [Common.jsonify(document) for document in list(paginated_cursor)]

        total = self.ref_tokens_collection.count_documents(query)

        return Output(
            output_details={
                'data': data,
                'total': total
            },
            output_message=""
        )
