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
        if firebase_admin._apps:
            apps = list(firebase_admin._apps.keys())
            for app_name in apps:
                app = firebase_admin.get_app(app_name)
                firebase_admin.delete_app(app)
        cred = credentials.Certificate(cred_file_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://sukoonlove-007-default-rtdb.firebaseio.com/'
        })

    def upsert_expert(self) -> None:
        self.initialize_firebase_admin()
        ref = db.reference('/experts')

        expert_ref = ref.child(str(self.expert._id))
        expert_ref.update({
            'status': self.expert.status,
            'isBusy': self.expert.isBusy
        })
