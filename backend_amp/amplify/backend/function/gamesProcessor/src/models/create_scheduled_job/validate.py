from models.interfaces import CreateScheduledJobInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):

        # if not self.input.job_time:
        #     return False, "Job Time is Mandatory"

        # if not self.input.job_type:
        #     return False, "Job Type is Mandatory"
        
        # if not self.input.status:
        #     return False, "Status is Mandatory"
        
        # if not self.input.request_meta:
        #     return False, "Request Meta is Mandatory"
        
        return True, ""
    

    