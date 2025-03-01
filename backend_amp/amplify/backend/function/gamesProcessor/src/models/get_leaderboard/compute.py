from shared.models.interfaces import GetLeaderBoardInput as Input, Output
from shared.db.games import get_game_saves_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.collection = get_game_saves_collection()

    def __format__(self, entry: dict) -> dict:
        entry['user_name'] = self.common.get_user_name(entry['_id'])
        return Common.jsonify(entry)

    def compute(self) -> Output:
        pipeline = [
            {"$match": {"game_type": self.input.game_type}},
            {"$group": {"_id": "$user_id", "total_score": {"$sum": "$score"}}},
            {"$sort": {"total_score": -1}}
        ]
        if self.input.page and self.input.size:
            page = int(self.input.page)
            size = int(self.input.size)
            pipeline.append({"$skip": (page - 1) * size})
            pipeline.append({"$limit": size})

        leaderboard = self.collection.aggregate(pipeline)
        leaderboard = [self.__format__(entry) for entry in list(
            leaderboard)] if leaderboard else []

        return Output(
            output_details=leaderboard
        )
