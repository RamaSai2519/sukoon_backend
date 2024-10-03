import re
import json

def extract_json(format_spec: str) -> dict:
    if "json" in format_spec:
        response_text = re.search(
            r'```json\n(.*?)```', format_spec, re.DOTALL)
        if response_text:
            response_text = response_text.group(1)
            response_text = response_text.replace("\n", "")
            return json.loads(response_text)    
    return json.loads(format_spec)