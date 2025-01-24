from shared.models.interfaces import UpsertPRCInput as Input, Output
from shared.db.referral import get_prcs_collection
from shared.models.common import Common
import hashlib
import random
import string


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_prcs_collection()

    def validate_prc(self, code: str) -> bool:
        query = {'token': code}
        prc_doc = self.collection.find_one(query)
        return prc_doc if prc_doc else False

    def generate_prc(self, name: str) -> str:
        salt = ''.join(random.choices(string.ascii_letters, k=6))
        raw_data = name + salt
        hash_object = hashlib.sha256(raw_data.encode())
        code = hash_object.hexdigest()[:8].upper()
        valid_code = self.validate_prc(code)
        return code if not valid_code else self.generate_prc(name)

    def validate_name(self, name: str) -> bool:
        query = {'name': name}
        prc_doc = self.collection.find_one(query)
        return prc_doc if prc_doc else False

    def compute(self) -> Output:
        doc = self.input.__dict__
        if self.input.token:
            query = {'token': self.input.token}
        else:
            query = {'name': self.input.name}
            if not self.input.token and not self.validate_name(self.input.name):
                self.input.token = self.generate_prc(self.input.name)
            else:
                doc.pop('token')

        upsert = self.collection.find_one_and_update(
            query,
            {"$set": doc},
            upsert=True,
            return_document=True
        )

        return Output(
            output_details=Common.jsonify(upsert),
            output_message="Referral Token Upserted",
        )
