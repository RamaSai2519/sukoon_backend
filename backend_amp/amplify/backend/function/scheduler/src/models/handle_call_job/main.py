import traceback
from shared.models.constants import OutputStatus
from models.handle_call_job.compute import Compute
from shared.models.interfaces import Output, Schedule


class CallJobHandler:
    def __init__(self, input: Schedule) -> None:
        self.input = input

    def process(self) -> Output:
        try:
            output = self._compute()
        except Exception as e:
            print(traceback.format_exc())
            output = Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"{e}",
            )

        return output

    def _compute(self) -> Output:
        computation_obj = Compute(self.input)
        output = computation_obj.compute()

        return output
