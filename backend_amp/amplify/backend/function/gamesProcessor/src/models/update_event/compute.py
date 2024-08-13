import dataclasses
from db_queries.mutations.event import update_event
from models.interfaces import EventInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self):
        if self.input.action == "UPDATE":
            # Convert the EventInput object to a dictionary
            event_data = dataclasses.asdict(self.input)
            # Remove the 'action' field
            event_data.pop('action', None)

            # Pass the dictionary to the update_event function
            response = update_event(event_data)

            return Output(
                output_details=response,
                output_status="SUCCESS",
                output_message="Successfully updated event"
            )

        if self.input.action == "DELETE":
            # Handle the DELETE action
            update_event(
                {
                    "id": self.input.id,
                    "isDeleted": True
                }
            )
            return Output(
                output_details=response,
                output_status="SUCCESS",
                output_message="Successfully updated event"
            )
