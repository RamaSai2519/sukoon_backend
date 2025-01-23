from shared.models.interfaces import GetEscalationsInput as Input, Output
from shared.db.calls import get_escalations_collection
from shared.models.constants import TimeFormats
from shared.models.common import Common
from datetime import datetime
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_escalations_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)

        object_id_fields = ['_id', 'user_id',
                            'expert_id', 'escalations.expert_id']
        for field in object_id_fields:
            if self.input.filter_field == field:
                query[field] = ObjectId(self.input.filter_value)

        time_fields = ['created_at', 'updated_at', 'escalations.time']
        for field in time_fields:
            if self.input.filter_field == field:
                query[field] = datetime.strptime(
                    self.input.filter_value, TimeFormats.ANTD_TIME_FORMAT)

        int_fields = ['escalations.level']
        for field in int_fields:
            if self.input.filter_field == field:
                query[field] = int(self.input.filter_value)

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
                'data': data,
                'total': total
            },
            output_message="Data fetched successfully"
        )
