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

        return Output(
            output_message="Data fetched successfully"
        )
