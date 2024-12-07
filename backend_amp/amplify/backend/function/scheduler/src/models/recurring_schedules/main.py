import traceback
from shared.models.interfaces import Output
from shared.models.constants import OutputStatus
from models.recurring_schedules.compute import Compute


class RecurringSchedules:
    def __init__(self) -> None:
        pass

    def process(self, time: str) -> Output:
        try:
            output = self._compute(time)
        except Exception as e:
            print(traceback.format_exc())
            output = Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"{e}",
            )

        return output

    def _compute(self, time: str) -> Output:
        computation_obj = Compute(time)
        output = computation_obj.compute()

        return output
