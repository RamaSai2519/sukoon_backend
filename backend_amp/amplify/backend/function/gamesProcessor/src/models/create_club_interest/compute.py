from db.users import get_club_interests_collection, get_user_collection
from models.interfaces import CreateClubInterestInput as Input, Output, ClubInterest
from models.constants import OutputStatus
from models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.collection = get_club_interests_collection()

    def compute(self) -> Output:
        club_interest = ClubInterest(
            userId=self.input.user_id,
            isInterested=self.input.isInterested,
        )
        data = club_interest.__dict__
        data = {k: v for k, v in data.items() if v is not None}
        self.collection.insert_one(data)

        return Output(
            output_status=OutputStatus.SUCCESS,
            output_message="Interest created successfully",
            output_details=Common.jsonify(data)
        )
