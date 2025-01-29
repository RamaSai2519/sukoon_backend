from shared.db.misc import get_counters_collection
from shared.configs import DevConfig, MainConfig
from shared.configs import CONFIG as config
from shared.models.interfaces import Output
from pymongo.collection import Collection
from shared.models.common import Common
from pymongo import MongoClient
from datetime import datetime
import pytz


class Compute:
    def __init__(self) -> None:
        self.url = config.URL
        self.now_time = self.get_now_time()
        self.collection = get_counters_collection()

    def get_now_time(self) -> datetime:
        timezone = pytz.timezone("Asia/Kolkata")
        current_time = datetime.now(timezone)
        return current_time

    def insert_docs(self, dev_collection: Collection, prod_collection: Collection, collection: str) -> None:
        print(f'Copying {collection} from prod to dev')
        docs = prod_collection.find().sort('_id', -1)
        if 'user' not in collection:
            docs.limit(1000)
        docs = list(docs)
        if docs and len(docs) > 0:
            update = dev_collection.insert_many(docs)
            msg = f'Copied {len(update.inserted_ids)} docs'
        else:
            msg = f'No documents found in {dev_collection}'
        return msg

    def check_last_triggered(self, collection: str) -> bool:
        current_time = Common.get_current_utc_time()
        query = {'name': 'db_backup'}
        doc: dict = self.collection.find_one(query)
        if not doc:
            doc = {'name': 'db_backup', collection: self.now_time}
            self.collection.insert_one(doc)
            return True
        last_triggered: datetime = doc.get(collection)
        if not last_triggered:
            update = {'$set': {collection: current_time}}
            self.collection.update_one(query, update)
            return True
        last_triggered = last_triggered.replace(tzinfo=pytz.utc)
        if not last_triggered:
            update = {'$set': {collection: current_time}}
            self.collection.update_one(query, update)
            return True
        difference = current_time - last_triggered
        if difference.days < 1:
            return False
        update = {'$set': {collection: current_time}}
        self.collection.update_one(query, update)
        return True

    def job(self) -> list:
        msgs = []
        prod_client = MongoClient(MainConfig.DB_CONFIG['connection_url'])
        dev_client = MongoClient(DevConfig.DB_CONFIG['connection_url'])
        dbs = prod_client.list_database_names()
        for db_name in dbs:
            prod_db = prod_client[db_name]
            dev_db = dev_client[db_name]
            prod_collections = list(prod_db.list_collection_names())
            for collection in prod_collections:
                if self.check_last_triggered(collection) is False:
                    msgs.append(f'{collection} already copied today')
                    continue
                prod_collection = prod_db.get_collection(collection)
                dev_collection = dev_db.get_collection(collection)
                dev_collection.drop()
                msg = self.insert_docs(
                    dev_collection, prod_collection, collection)
                self.collection.update_one(
                    {'name': 'db_backup'},
                    {'$set': {collection: self.now_time}}
                )
                msgs.append(msg)
        return msgs

    def compute(self) -> list:
        print(f"Current Time: {self.now_time}")
        msg = self.job()
        print(msg)
        return Output(output_status="SUCCESS", output_message="Job executed successfully")
