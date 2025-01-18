from shared.models.interfaces import GetLeadsCountInput as Input
from shared.models.constants import CallStatus


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.status_list = [
            value for name, value in CallStatus.__dict__.items() if not name.startswith('__')]

    def validate_input(self) -> tuple:
        
        if self.input.call_status not in self.status_list:
            return False, "Invalid call status"
        
        return True, ""

    
    