from shared.models.constants import OutputStatus, exclude_deleted_query
from shared.models.interfaces import GetExpertsInput as Input, Output
from shared.db.experts import get_categories_collection
from shared.db.calls import get_schedules_collection
from shared.helpers.experts import ExpertsHelper
from shared.models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.helper = ExpertsHelper()
        self.schedules_collection = get_schedules_collection()
        self.categories_collection = get_categories_collection()

    # def populate_schedules(self, expert: dict) -> dict:
    #     query = {"expert": ObjectId(
    #         expert["_id"]), "status": self.input.schedule_status}
    #     expert[f"{self.input.schedule_status}_schedules"] = self.common.get_schedules(
    #         query)
    #     query = {"expert": ObjectId(expert["_id"])}
    #     expert["schedule_counts"] = self.common.get_schedules_counts(query)
    #     return expert

    def compute(self) -> Output:
        if self.input.phoneNumber is not None or self.input.expert_id is not None:
            experts = self.helper.get_expert(
                self.input.phoneNumber, self.input.expert_id)
            if not experts:
                return Output(
                    output_details={},
                    output_status=OutputStatus.FAILURE,
                    output_message="Expert not found"
                )
            # if self.input.schedule_status is not None:
            #     experts = self.populate_schedules(experts)
        else:
            query = self.common.get_internal_exclude_query(
                self.input.internal, "_id")
            if self.input.filter_field == 'categories':
                filter_query = self.common.get_filter_query(
                    'name', self.input.filter_value)
                cats = list(self.categories_collection.find(filter_query))
                cat_ids = [str(cat['_id']) for cat in cats]
                filter_query = {'categories': {'$in': cat_ids}}
                query = {**filter_query, **query}
            else:
                filter_query = self.common.get_filter_query(
                    self.input.filter_field, self.input.filter_value)
                query = {**filter_query, **query}

            query = {**query, **exclude_deleted_query}
            experts = self.helper.get_experts(query)

        return Output(
            output_details=experts,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched expert(s)"
        )
