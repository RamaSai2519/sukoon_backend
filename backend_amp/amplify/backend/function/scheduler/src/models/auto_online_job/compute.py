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
        self.common = Common()
        self.collection = get_experts_collections()
        self.now_time = Common.get_current_ist_time()
        self.timings_collection = get_timings_collection()

    def job(self, expert_id: ObjectId, timing_id: ObjectId) -> bool:
        target_time = Common.get_current_utc_time() + timedelta(hours=1)
        expert = self.collection.find_one(
            {'_id': expert_id})
        if not expert or expert.get('isDeleted', False) is True:
            return
        expert_phone = expert['phoneNumber']
        url = config.URL + '/actions/expert'
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

    def handle_new_experts(self):
        query = {'next_update': {'$exists': False}}
        docs = list(self.timings_collection.find(query))
        if len(docs) == 0:
            return
        self.timings_collection.update_many(
            {'_id': {'$in': [doc['_id'] for doc in docs]}},
            {'$set': {'next_update': Common.get_current_utc_time()}}
        )
        return

    def compute(self) -> Output:
        self.handle_new_experts()
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
        print(docs)
        for doc in docs:
            expert_id = doc['expert']
            timing_id = doc['_id']
            if not self.common.check_vacation(expert_id):
                continue
            job_status = self.job(expert_id, timing_id)
            if job_status:
                print('Expert: ', expert_id, ' is online')

        return Output()
