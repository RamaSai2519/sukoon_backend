from shared.db.content import get_blogposts_collection
from shared.models.interfaces import GetBlogPostsInput as Input, Output
from shared.models.common import Common
from shared.models.constants import OutputStatus

class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.blogposts_collection = get_blogposts_collection()

    def compute(self) -> Output:
        query = {}
        if self.input.title:
            query["title"] = {"$regex": self.input.title, "$options": "i"}  
        if self.input.tags:
            query["tags"] = {"$in": self.input.tags}  

        cursor = self.blogposts_collection.find(query)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size)
        )

        data = [Common.jsonify(document) for document in list(paginated_cursor)]
        total = self.blogposts_collection.count_documents(query)

        return Output(
            output_details={"data": data, "total": total},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully retrieved blog posts"
        )
