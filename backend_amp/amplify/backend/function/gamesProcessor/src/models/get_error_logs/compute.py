from models.interfaces import GetErrorLogsInput as Input, Output
from db.admins import get_error_logs_collection
from models.constants import OutputStatus
from models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_error_logs_collection()

    def compute(self) -> Output:
        cursor = self.collection.find().sort("time", -1)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size))
        data = [Common.jsonify(spec) for spec in paginated_cursor]
        total_count = self.collection.count_documents({})

        return Output(
            output_status=OutputStatus.SUCCESS,
            output_message="Data fetched successfully",
            output_details={"data": data, "total": total_count}
        )
