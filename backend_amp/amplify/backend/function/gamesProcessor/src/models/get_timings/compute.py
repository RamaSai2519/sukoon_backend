from bson import ObjectId
from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.db.experts import get_timings_collection
from shared.models.interfaces import GetTimingsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.timings_collection = get_timings_collection()

    def fetch_timings(self) -> list:
        query = {
            "expert": ObjectId(self.input.expert)
        }
        timings = list(self.timings_collection.find(query))
        timings = [Common.jsonify(timing) for timing in timings]
        return timings

    def compute(self) -> Output:
        timings = self.fetch_timings()

        return Output(
            output_details=timings,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched referral(s)"
        )
