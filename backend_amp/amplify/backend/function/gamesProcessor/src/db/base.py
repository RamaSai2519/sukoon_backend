from pymongo import MongoClient
import certifi
from configs import CONFIG as config


class Database:
    _instance = None
    _client = None

    def __init__(self) -> None:
        self.url = config.DB_CONFIG.get("connection_url")

    def __new__(cls) -> "Database":
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    @property
    def client(self) -> MongoClient:
        if self._client is None:
            try:
                self._client = MongoClient(self.url, tlsCAFile=certifi.where())
            except Exception as e:
                print(f"Error initializing MongoDB client: {e}")
        return self._client
