from config import main_lambda_url as url
import requests
import json


def updater(expert_id: str, expert_number: str) -> None:
    payload = json.dumps({
        "expert_id": expert_id,
        "expert_number": expert_number
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
