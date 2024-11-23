from bson import ObjectId
from shared.models.common import Common
from pymongo.results import UpdateResult
from shared.models.constants import OutputStatus
from shared.db.experts import get_timings_collection
from shared.models.interfaces import UpdateTimingsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.times = ["PrimaryStartTime", "PrimaryEndTime",
                      "SecondaryStartTime", "SecondaryEndTime"]
        self.timings_collection = get_timings_collection()

    def update_timing(self) -> UpdateResult:
        admin_Id = ObjectId(Common.get_identity())
        filter = {"expert": ObjectId(
            self.input.expertId), "day": self.input.row.key}
        query = {"$set": {self.input.row.field: self.input.row.value,
                          "lastModifiedBy": admin_Id}}
        update = self.timings_collection.update_one(filter, query)
        return update

    def compute(self) -> Output:
        self.update_timing()

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message="Timings updated successfully"
        )
