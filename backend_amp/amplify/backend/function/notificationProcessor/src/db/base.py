from pymongo import MongoClient
from configs import CONFIG as Config

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.client = MongoClient(Config.DB_CONFIG.get("connection_url"))
        return cls._instance

