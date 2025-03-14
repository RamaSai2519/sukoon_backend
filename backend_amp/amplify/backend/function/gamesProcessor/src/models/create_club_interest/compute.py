from shared.db.users import get_club_interests_collection, get_user_collection
from shared.models.interfaces import CreateClubInterestInput as Input, Output, ClubInterest
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.collection = get_club_interests_collection()

    def compute(self) -> Output:
        club_interest = ClubInterest(self.input.__dict__)
        data = club_interest.__dict__
        data = Common.filter_none_values(data)
        self.collection.insert_one(data)

        return Output(
            output_message="Interest created successfully",
            output_details=Common.jsonify(data)
        )
