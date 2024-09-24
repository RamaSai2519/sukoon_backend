from models.interfaces import GetExpertsInput as Input, Output
from db.calls import get_schedules_collection
from models.constants import OutputStatus
from helpers.experts import ExpertsHelper
from models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.helper = ExpertsHelper()
        self.schedules_collection = get_schedules_collection()

    def populate_schedules(self, expert: dict) -> dict:
        query = {"expert": ObjectId(
            expert["_id"]), "status": self.input.schedule_status}
        expert[f"{self.input.schedule_status}_schedules"] = self.common.get_schedules(
            query)
        query = {"expert": ObjectId(expert["_id"])}
        expert["schedule_counts"] = self.common.get_schedules_counts(query)
        return expert

    def compute(self) -> Output:
        if self.input.phoneNumber is not None:
            experts = self.helper.get_expert(self.input.phoneNumber)
            if not experts:
                return Output(
                    output_details={},
                    output_status=OutputStatus.FAILURE,
                    output_message="Expert not found"
                )
            if self.input.schedule_status is not None:
                experts = self.populate_schedules(experts)
        else:
            query = self.common.get_internal_exclude_query(
                self.input.internal, "_id")
            exclude_deleted_query = {
                "$or": [{"isDeleted": {"$exists": False}}, {"isDeleted": False}]
            }
            query = {**query, **exclude_deleted_query}
            experts = self.helper.get_experts(query)

        return Output(
            output_details=experts,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched expert(s)"
        )
