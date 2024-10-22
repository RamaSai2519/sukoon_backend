class OutputStatus:
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


class CallStatus:
    MISSED = 'missed'
    FAILED = 'failed'
    SUCCESSFUL = 'successful'
    INADEQUATE = 'inadequate'


calls_exclusion_projection = {
    'user': 1,
    'callId': 1,
    'expert': 1,
    'status': 1,
    'duration': 1,
    'failedReason': 1,
    'initiatedTime': 1,
    'recording_url': 1,
    'lastModifiedBy': 1,
    'user_requested': 1,
    'conversationScore': 1,
}


successful_calls_query = {
    'failedReason': '',
    'status': 'successful'
}

application_json_header = {'Content-Type': 'application/json'}

meta_fields = ['remarks', 'expert', 'lastReached',
               'status', 'userStatus', 'source']

indianLanguages = [
    {'key': 'as', 'value': 'Assamese'},
    {'key': 'bn', 'value': 'Bengali'},
    {'key': 'brx', 'value': 'Bodo'},
    {'key': 'doi', 'value': 'Dogri'},
    {'key': 'gu', 'value': 'Gujarati'},
    {'key': 'hi', 'value': 'Hindi'},
    {'key': 'kn', 'value': 'Kannada'},
    {'key': 'ks', 'value': 'Kashmiri'},
    {'key': 'kok', 'value': 'Konkani'},
    {'key': 'mai', 'value': 'Maithili'},
    {'key': 'ml', 'value': 'Malayalam'},
    {'key': 'mni', 'value': 'Manipuri'},
    {'key': 'mr', 'value': 'Marathi'},
    {'key': 'ne', 'value': 'Nepali'},
    {'key': 'or', 'value': 'Odia'},
    {'key': 'pa', 'value': 'Punjabi'},
    {'key': 'sa', 'value': 'Sanskrit'},
    {'key': 'sat', 'value': 'Santali'},
    {'key': 'sd', 'value': 'Sindhi'},
    {'key': 'ta', 'value': 'Tamil'},
    {'key': 'te', 'value': 'Telugu'},
    {'key': 'ur', 'value': 'Urdu'}
]

extract_json_function_str = r"""```python
def extract_json(json_str: str) -> dict:
    def clean_json(json_str: str) -> str:
        json_str = json_str.replace("\n", "").replace("```", "").replace("json", "").strip()
        return json_str

    try:
        if "json" in json_str:
            match = re.search(r'```json\n(.*?)```', json_str, re.DOTALL)
            if match:
                response_text = clean_json(match.group(1))
                response_text = json.loads(response_text)
                return response_text
        cleaned_json_str = clean_json(json_str)
        cleaned_json_str = json.loads(cleaned_json_str)
        return cleaned_json_str
    except Exception as e:
        print(e)
        return json_str
```"""
