from models.interfaces import GetUserInput as Input, Output
from models.constants import OutputStatus
from db_queries.queries.user import fetch_user_by_mobile_number


class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input
    
    def _check_if_user_exist_with_this_mobile_number(self) -> None:
        
        query_result = fetch_user_by_mobile_number(self.input.mobile_number)
        if not query_result:
            return False
        
        user_array = query_result.get("items")

        if not user_array:
            return False
        
        return user_array[0]
        
    def compute(self):

        user = self._check_if_user_exist_with_this_mobile_number()
        user_exist = True if user else False

        return Output(
            output_details={"user_exists": user_exist},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched user"
        )