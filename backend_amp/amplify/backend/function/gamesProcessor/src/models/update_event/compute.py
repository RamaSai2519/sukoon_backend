from db_queries.mutations.event import update_event, delete_event
from models.interfaces import EventInput as Input, Output


class Compute:
    def __init__(self, input:Input) -> None:
        self.input = input

    def compute(self):
        if self.input.action == "UPDATE":
            update_event(self.input)
        if self.input.action == "DELETE":
            update_event(
                {
                    "id": self.input.id,
                    "isDeleted": True
                }
            )

        return Output(
            output_details="",
            output_status="SUCCESS",
            output_message="Successfully updated event"
        )
