from models.interfaces import FetchShortsInput as Input, Output
from models.constants import OutputStatus
from db.shorts import get_shorts_collections, get_shorts_categories_collections
from bson import ObjectId

from datetime import datetime
from db.experts import get_experts_collections

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input

    def _process_shorts(self, shorts):
        category_id = shorts[0].get("categoryId")
        category = get_shorts_categories_collections().find_one({"_id": ObjectId(category_id)})
        experts_array = category.get("experts")
        length_of_experts_array = len(experts_array)

        counter = 1
        for short in shorts:
            expert_id = experts_array[counter%length_of_experts_array]
            counter +=1
            expert = get_experts_collections().find_one({"_id": ObjectId(expert_id)})
            expert_video_link = expert.get("shortLink", "")
            expert_video_name = expert.get("name", "")
            short["expertVideoLink"] = expert_video_link
            short["expertVideoName"] = expert_video_name
            short["createdAt"] = short.get("createdAt").strftime('%Y-%m-%d %H:%M:%S')
            del short['categoryId']
        self.shorts.append(shorts)

    def _get_shorts(self) -> dict:
        shorts_collection = get_shorts_collections()

        
        if not self.input.fetchedTill:
            keywords = ["Daily Tips", "News of the day", "Life messages"]
            for keyword in keywords:
                shorts = list(shorts_collection.find({"keyword": keyword}, {"_id": 0, "thumbnails": 0, "description": 0}).sort({ "createdAt": -1 }).limit(3))
                self._process_shorts(shorts)
        else:
            for item in self.input.fetchedTill:
                keyword = item.get("keyword")
                timestamp = item.get("fetchedTillDateTime")
                timestamp = datetime.strptime(timestamp , '%Y-%m-%d %H:%M:%S')
                shorts = list(shorts_collection.find({"keyword": keyword, "createdAt": { "$gt": timestamp } }, {"_id": 0, "thumbnails": 0, "description": 0}).sort({ "createdAt": -1 }).limit(3))
                self._process_shorts(shorts)

    def compute(self):

        self.shorts = []
        self._get_shorts()

        return Output(
            output_details={"shorts": self.shorts},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )