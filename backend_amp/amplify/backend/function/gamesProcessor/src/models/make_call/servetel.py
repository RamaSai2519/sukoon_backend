import requests
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.db.experts import get_sagents_collection
from shared.models.interfaces import CallerInput as Input


class MakeServeTelCall:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.sagents_collection = get_sagents_collection()
        self.api_key = self.get_agent_api_key()

    def get_agent_api_key(self) -> str:
        query = {'phoneNumber': self.input.expert_number}
        doc = self.sagents_collection.find_one(query)
        if not doc:
            cursor = self.sagents_collection.find()
            earliest = cursor.sort('updatedAt', 1).limit(1)
            doc = list(earliest)[0]
            agent_id = doc['id']

            url = config.SERVETEL_API_CONFIG['base_url'] + \
                f'/user/{agent_id}'
            payload = {'number': self.input.expert_number}
            headers = {
                'Authorization': 'Bearer ' + config.SERVETEL_API_CONFIG['token']
            }
            response = requests.patch(url, headers=headers, json=payload)
            print(response.text, '__servetel_response__')
            if response.status_code != 200:
                raise Exception('Error getting agent api key')

            self.sagents_collection.update_one(
                {'id': agent_id},
                {'$set': {'phoneNumber': self.input.expert_number,
                          'updatedAt': Common.get_current_utc_time()}}
            )

        return doc['api_key']

    def _make_call(self) -> None:
        url = config.SERVETEL_API_CONFIG['base_url'] + '/click_to_call_support'
        payload = {
            'customer_number': self.input.user_number,
            'api_key': self.api_key,
            'suid': self.input.call_id
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            return False, {}
        else:
            print(response.json())
            return True, response.json()
