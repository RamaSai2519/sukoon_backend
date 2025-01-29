from shared.db.experts import get_experts_collections, get_timings_collection
from shared.models.constants import TimeFormats
from shared.models.interfaces import Output
from shared.configs import CONFIG as config
from shared.models.common import Common
from datetime import timedelta
from bson import ObjectId
import requests


class Compute:
    def __init__(self) -> None:
        self.collection = get_experts_collections()
        self.now_time = Common.get_current_ist_time()
        self.timings_collection = get_timings_collection()

    def job(self, expert_id: ObjectId, timing_id: ObjectId) -> bool:
        target_time = Common.get_current_utc_time() + timedelta(hours=1)
        expert = self.collection.find_one(
            {'_id': expert_id})
        if not expert:
            return
        expert_phone = expert['phoneNumber']
        url = config.URL
        payload = {
            'phoneNumber': expert_phone,
            'status': 'online'
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            self.timings_collection.update_one(
                {'_id': timing_id},
                {'$set': {'next_update': target_time}}
            )
            return True
        return False

    def compute(self) -> Output:
        today = self.now_time.strftime("%A")
        ctime = self.now_time.replace(minute=0)
        hour = ctime.strftime(TimeFormats.HOURS_24_FORMAT)
        current_time = Common.get_current_utc_time()
        query = {
            'day': today,
            'next_update': {'$lt': current_time},
            '$or': [
                {'PrimaryStartTime': hour},
                {'SecondaryStartTime': hour}
            ]
        }
        docs = list(self.timings_collection.find(query))
        for doc in docs:
            expert_id = doc['expert']
            timing_id = doc['_id']
            job_status = self.job(expert_id, timing_id)
            if job_status:
                print('Expert: ', expert_id, ' is online')

        return Output()
