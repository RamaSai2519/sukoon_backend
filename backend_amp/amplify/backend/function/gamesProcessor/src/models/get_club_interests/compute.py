from shared.db.users import get_club_interests_collection, get_user_collection
from shared.models.interfaces import GetClubInterestsInput as Input, Output
from shared.models.constants import OutputStatus
from shared.models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.collection = get_club_interests_collection()

    def __format__(self, spec: dict) -> dict:
        user_query = {"_id": ObjectId(spec["userId"])}
        projection = {"_id": 0, "name": 1, "phoneNumber": 1}
        user = self.users_collection.find_one(user_query, projection)
        if user:
            spec["name"] = user["name"]
            spec["phoneNumber"] = user["phoneNumber"]
        else:
            self.collection.delete_one({"_id": spec["_id"]})
        return Common.jsonify(spec)

    def compute(self) -> Output:
        cursor = self.collection.find().sort("createdAt", -1)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size))
        data = [self.__format__(spec) for spec in paginated_cursor]
        total_count = self.collection.count_documents({})

        return Output(
            output_status=OutputStatus.SUCCESS,
            output_message="Data fetched successfully",
            output_details={"data": data, "total": total_count}
        )
