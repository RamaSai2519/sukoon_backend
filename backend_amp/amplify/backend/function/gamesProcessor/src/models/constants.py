class OutputStatus:
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


calls_exclusion_projection = {
    "user": 1,
    "callId": 1,
    "expert": 1,
    "status": 1,
    "duration": 1,
    "failedReason": 1,
    "initiatedTime": 1,
    "lastModifiedBy": 1,
    "Conversation Score": 1
}


successful_calls_query = {
    "failedReason": "",
    "status": "successfull"
}

application_json_header = {"Content-Type": "application/json"}
