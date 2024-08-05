from models.interfaces import CreateNonRegisteredUserInput as Input, Output
from models.constants import OutputStatus
from db_queries.mutations.event import update_event, create_event

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input


    def _update_event(self):

        event_data = {
            # "id": user_id,
            "dateOfBirth": self.input.date_of_birth,
            "firstName": self.input.first_name,
            "gender": self.input.gender,
            "status": UserStatus.REGISTERED.name,
            "lastName": self.input.last_name,
            "mobileNumber": self.input.mobile_number,
        }

        update_event(event_data)


    def _create_event(self):
        pass
    

    def compute(self):

        action = self.input.action
        if action == "UPDATE":
            self._update_event()
            
        else:
            self._create_event()

        return Output(
            output_details="",
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully created non registered user"
        )