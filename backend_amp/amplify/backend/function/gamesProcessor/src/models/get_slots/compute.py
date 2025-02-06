from shared.models.constants import OutputStatus
from shared.models.interfaces import GetSlotsInput as Input, Output
from models.get_slots.slot import Slot


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self) -> Output:
        slot = Slot(
            expert_id=self.input.expert,
            utc_date=self.input.datetime,
            duration=self.input.duration
        )
        print(slot, '__slot__')
        output_slots = slot.to_output_slots()

        return Output(
            output_details=output_slots,
            output_status=OutputStatus.SUCCESS,
            output_message="Slots fetched successfully"
        )
