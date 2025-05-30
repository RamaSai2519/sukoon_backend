from shared.models.constants import OutputStatus, exclude_deleted_query
from shared.models.interfaces import GetExpertsInput as Input, Output
from shared.db.schedules import get_schedules_collection
from shared.helpers.experts import ExpertsHelper
from shared.models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.helper = ExpertsHelper()
        self.schedules_collection = get_schedules_collection()

    def compute(self) -> Output:
        if self.input.phoneNumber is not None or self.input.expert_id is not None:
            req_calls = False if self.input.req_calls == 'false' else True
            experts = self.helper.get_expert(
                self.input.phoneNumber, self.input.expert_id, req_calls,
                int(self.input.calls_page), int(self.input.calls_size))
            if not experts:
                return Output(
                    output_status=OutputStatus.FAILURE,
                    output_message="Expert not found"
                )
        else:
            query = self.common.get_internal_exclude_query(
                self.input.internal, "_id")
            if self.input.filter_field == "sub_category":
                category_ids = self.input.filter_value.split(",")
                category_ids = [ObjectId(v.strip()) for v in category_ids]
                self.input.filter_value = category_ids
                filter_query = {"sub_category": {
                    "$in": self.input.filter_value}}
            elif self.input.filter_field == "categories":
                category_ids = self.input.filter_value.split(",")
                category_ids = [ObjectId(v.strip()) for v in category_ids]
                self.input.filter_value = category_ids
                filter_query = {"categories": {
                    "$in": self.input.filter_value}}
            else:
                filter_query = self.common.get_filter_query(
                    self.input.filter_field, self.input.filter_value)

            query = {**filter_query, **query}
            query = {**query, **exclude_deleted_query}
            if not self.input.platform or self.input.platform.lower() == 'public':
                query['active'] = True

            experts = self.helper.get_experts(
                query, int(self.input.size), int(self.input.page))

        return Output(
            output_details=experts,
            output_message="Successfully fetched expert(s)"
        )
