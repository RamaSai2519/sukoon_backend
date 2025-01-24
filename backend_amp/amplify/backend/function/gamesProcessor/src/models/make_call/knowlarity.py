import requests
from shared.models.interfaces import CallerInput as Input


class MakeKnowlarityCall:
    def __init__(self, input: Input):
        self.input = input

    def _make_call(self) -> str:
        knowlarity_url = "https://kpi.knowlarity.com/Basic/v1/account/call/makecall"
        headers = {
            "x-api-key": "bb2S4y2cTvaBVswheid7W557PUzUVMnLaPnvyCxI",
            "authorization": "0738be9e-1fe5-4a8b-8923-0fe503e87deb"
        }
        payload = {
            "k_number": "+918035752993",
            "agent_number": "+91" + self.input.expert_numer,
            "customer_number": "+91" + self.input.user_number,
            "caller_id": "+918035752993"
        }
        response = requests.post(knowlarity_url, headers=headers, json=payload)

        if response.status_code != 200:
            print(response.json(), "Failed to make call")
            return False

        response_dict: dict = response.json()
        success: dict = response_dict.get("success", {})
        call_id = success.get("call_id", None)
        return call_id
