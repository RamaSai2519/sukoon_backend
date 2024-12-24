import pandas as pd
from datetime import datetime
from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.db.users import get_user_collection, get_meta_collection
from shared.models.interfaces import BulkUploadInput as Input, Output, User


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.meta_collection = get_meta_collection()

    def load_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.input.file_url)
        return data.to_dict(orient='records')

    def validate(self, record: dict) -> tuple:
        if len(str(record["Phone"])) != 10:
            return False, f"Phone number {record['Phone']} is invalid"

        query = {"phoneNumber": str(record["Phone"])}
        existing_user = self.users_collection.find_one(query)
        if existing_user:
            return False, f"User with phone number {record['Phone']} already exists"

        return True, ""

    def get_default(self) -> dict:
        user = User(
            isBusy=False, active=True, isPaidUser=False, numberOfCalls=3, numberOfGames=0, profileCompleted=False
        ).__dict__
        user = {k: v for k, v in user.items() if v is not None}
        return user

    def __format__(self, record: dict) -> dict:
        user = self.get_default()
        user['name'] = str(record["First Name"] + " " +
                           record["Last Name"]).strip()
        user['email'] = str(record.get("Email", "")).strip()

        try:
            user_joined_date = datetime.strptime(
                str(record["Registration Time"]), "%m/%d/%Y %I:%M:%S %p")
        except:
            user_joined_date = datetime.now()

        user['createdDate'] = user_joined_date
        user["phoneNumber"] = str(record["Phone"])

        return user

    def insert_user(self, user: dict) -> str:
        inserted_record = self.users_collection.insert_one(user)
        return inserted_record.inserted_id

    def insert_meta(self, user_id: str, record: dict) -> None:
        meta = {
            'user': user_id,
            'context': str(record.get("Webinar", "")).strip(),
            'source': 'zoom',
            'userStatus': '',
            'remarks': '',
        }
        insertion = self.meta_collection.insert_one(meta)
        return insertion.inserted_id

    def compute(self) -> Output:
        data = self.load_data()
        success = 0

        for record in data:
            isvalid, message = self.validate(record)
            if not isvalid:
                print(message)
                continue

            user = self.__format__(record)
            inserted_id = self.insert_user(user)

            self.insert_meta(inserted_id, record)
            success += 1

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message=f"Successfully created {success} users"
        )
