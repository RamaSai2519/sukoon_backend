from models.interfaces import CreateContributeInterestInput as Input, Output, ContributeInterest
from db.events import get_contirbute_event_users_collection
from models.constants import OutputStatus
from models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_contirbute_event_users_collection()

    def compute(self) -> Output:
        club_interest = ContributeInterest(
            slug=self.input.slug,
            user_id=ObjectId(self.input.user_id)
        )
        data = club_interest.__dict__
        data = {k: v for k, v in data.items() if v is not None}
        self.collection.insert_one(data)

        return Output(
            output_status=OutputStatus.SUCCESS,
            output_message="Interest created successfully",
            output_details=Common.jsonify(data)
        )
