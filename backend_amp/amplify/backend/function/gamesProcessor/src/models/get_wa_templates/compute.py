from bson import ObjectId
from shared.models.common import Common
from shared.db.whatsapp import get_whatsapp_templates_collection
from shared.models.interfaces import GetWaRefsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_whatsapp_templates_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)
        if self.input.filter_field == '_id':
            query = {'_id': ObjectId(self.input.filter_value)}
        total = self.collection.count_documents(query)
        if total <= 10:
            self.input.page = 1
            self.input.size = total
        cursor = self.collection.find(query)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size))
        data = list(paginated_cursor)

        return Output(
            output_details={
                'data': Common.jsonify(data),
                'total': total
            },
            output_message="Successfully fetched data"
        )
