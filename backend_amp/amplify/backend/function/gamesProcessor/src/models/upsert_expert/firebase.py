from shared.models.interfaces import Expert
from firebase_admin import credentials, db
import firebase_admin
import os


class Firebase:
    def __init__(self, expert: Expert) -> None:
        self.expert = expert

    def initialize_firebase_admin(self) -> None:
        cred_file_path = os.path.join(os.path.dirname(
            __file__), 'sukoonlove-007-firebase.json')
        cred = credentials.Certificate(cred_file_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://sukoonlove-007-default-rtdb.firebaseio.com/'
        })

    def upsert_expert(self) -> None:
        self.initialize_firebase_admin()
        ref = db.reference('/experts')

        ref.set({
            str(self.expert._id): {
                'status': self.expert.status,
                'isBusy': self.expert.isBusy
            }
        })
