from shared.db.experts import get_experts_collections, get_timings_collection, get_vacations_collection
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
        self.vacations_collection = get_vacations_collection()

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

    def check_vacation(self, expert_id: ObjectId, hour: str) -> bool:
        query = {}
        query['user'] = expert_id
        current_time = Common.get_current_utc_time()
        query['start_date'] = {'$lte': current_time}
        query['end_date'] = {'$gte': current_time}
        query['isDeleted'] = False
        doc = self.vacations_collection.find_one(query)
        if not doc:
            return True
        start_time: str = doc.get('start_time', '')
        end_time: str = doc.get('end_time', '')
        if start_time != '' and end_time != '':
            start_hour = start_time.split(':')[0]
            end_hour = end_time.split(':')[0]
            hour = hour.split(':')[0]
            if int(start_hour) <= int(hour) <= int(end_hour):
                print('Expert:', expert_id, 'is on vacation')
                return False
        return True

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
        print(docs)
        for doc in docs:
            expert_id = doc['expert']
            timing_id = doc['_id']
            if not self.check_vacation(expert_id, hour):
                continue
            job_status = self.job(expert_id, timing_id)
            if job_status:
                print('Expert: ', expert_id, ' is online')

        return Output()
