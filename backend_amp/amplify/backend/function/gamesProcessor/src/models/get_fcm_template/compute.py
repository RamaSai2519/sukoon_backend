from shared.models.interfaces import GetFCMTemplatesInput as Input, Output
from shared.db.users import get_fcm_templates_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.templates_collection = get_fcm_templates_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)

        cursor = self.templates_collection.find(query)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size)
        )

        data = [Common.jsonify(d) for d in list(paginated_cursor)]
        total = self.templates_collection.count_documents(query)

        return Output(
            output_details={
                'data': data,
                'total': total
            },
            output_message=""
        )
