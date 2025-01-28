from shared.models.interfaces import GetBetaTestersInput as Input, Output
from shared.db.misc import get_beta_testers_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_beta_testers_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value
        )

        total = self.collection.count_documents(query)
        if total <= 10:
            self.input.page = 1
            self.input.size = total
        cursor = self.collection.find(query)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size)
        )
        data = [Common.jsonify(list(paginated_cursor))]

        return Output(
            output_message="Data fetched successfully",
            output_details={"data": data, "total": total}
        )
