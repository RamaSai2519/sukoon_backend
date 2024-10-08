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
    "user_requested": 1,
    "Conversation Score": 1,
}


successful_calls_query = {
    "failedReason": "",
    "status": "successfull"
}

application_json_header = {"Content-Type": "application/json"}

meta_fields = ["remarks", "expert", "lastReached",
               "status", "userStatus", "source"]

indianLanguages = [
    {"key": "as", "value": "Assamese"},
    {"key": "bn", "value": "Bengali"},
    {"key": "brx", "value": "Bodo"},
    {"key": "doi", "value": "Dogri"},
    {"key": "gu", "value": "Gujarati"},
    {"key": "hi", "value": "Hindi"},
    {"key": "kn", "value": "Kannada"},
    {"key": "ks", "value": "Kashmiri"},
    {"key": "kok", "value": "Konkani"},
    {"key": "mai", "value": "Maithili"},
    {"key": "ml", "value": "Malayalam"},
    {"key": "mni", "value": "Manipuri"},
    {"key": "mr", "value": "Marathi"},
    {"key": "ne", "value": "Nepali"},
    {"key": "or", "value": "Odia"},
    {"key": "pa", "value": "Punjabi"},
    {"key": "sa", "value": "Sanskrit"},
    {"key": "sat", "value": "Santali"},
    {"key": "sd", "value": "Sindhi"},
    {"key": "ta", "value": "Tamil"},
    {"key": "te", "value": "Telugu"},
    {"key": "ur", "value": "Urdu"}
]
