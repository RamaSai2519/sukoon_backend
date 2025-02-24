from shared.db.experts import get_experts_collections
from shared.db.users import get_user_collection
from shared.configs import CONFIG as config
from shared.models.interfaces import Output
from shared.models.common import Common
from datetime import datetime
import requests
import json


class Compute:
    def __init__(self) -> None:
        self.url = config.URL
        self.now_time = Common.get_current_ist_time()
        self.target_time = self.get_target_time()
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()

    def get_target_time(self) -> datetime:
        return self.now_time.replace(hour=22, minute=0, second=0, microsecond=0)

    def job(self) -> list:
        query = {'status': 'online', 'type': {'$ne': 'agent'}}
        experts = list(self.experts_collection.find(query))
        messages = []
        for e in experts:
            payload = {'phoneNumber': e['phoneNumber'], 'status': 'offline'}
            url = self.url + '/actions/expert'
            response = requests.post(url, json=payload)
            response = json.loads(response.text)
            message = response.get('output_message')
            log = f"Expert: {e['phoneNumber']} Message: {message}"
            messages.append(log)

        self.users_collection.update_many({}, {'$set': {'isBusy': False}})
        self.experts_collection.update_many({}, {'$set': {'isBusy': False}})
        return messages

    def compute(self) -> list:
        print(f'Current Time: {self.now_time}')
        print(f'Target Time: {self.target_time}')
        if self.now_time > self.target_time:
            messages = self.job()
            return Output(output_details=messages, output_status='SUCCESS', output_message='Job executed successfully')
        return Output(output_status='FAILURE', output_message='Job not executed as it is not time yet or they were already triggered')
