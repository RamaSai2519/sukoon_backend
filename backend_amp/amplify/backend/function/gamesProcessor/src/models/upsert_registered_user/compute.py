from models.interfaces import UpsertRegisteredUserInput as Input, Output
from models.constants import OutputStatus
from models.enum import UserStatus
from db_queries.mutations.user import update_user
from db_queries.queries.user import fetch_user_by_mobile_number



class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input

    def _get_user_from_mobile_number(self) -> None:
        
        query_result = fetch_user_by_mobile_number(self.input.mobile_number)
        if not query_result:
            return False
        
        user_array = query_result.get("items")
        if not user_array:
            return False
        
        return user_array[0]
    
    def _update_user_details(self, user_id):

        user_data = {
            "id": user_id,
            "dateOfBirth": self.input.date_of_birth,
            "firstName": self.input.first_name,
            "gender": self.input.gender,
            "status": UserStatus.REGISTERED.name,
            "lastName": self.input.last_name,
            "mobileNumber": self.input.mobile_number,
        }

        update_user(user_data)

    def compute(self):
        user = self._get_user_from_mobile_number()

        user_id = user.get("id")

        if not user:

            return Output(
                output_details="",
                output_status=OutputStatus.FAILURE,
                output_message="No user found for this mobile number"
            )
        
        self._update_user_details(user_id)
        
        return Output(
            output_details="",
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully created non registered user"
        )