from models.common import Common
from models.constants import OutputStatus
from db.content import get_content_posts_collection
from models.interfaces import GetContentPostsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_content_posts_collection()

    def __format__(self, format_spec: list) -> list:
        return [Common.jsonify(post) for post in format_spec]

    def get_total_count(self) -> int:
        return self.collection.count_documents({})

    def compute(self) -> Output:
        cursor = self.collection.find()
        content_posts = list(Common.paginate_cursor(
            cursor, self.input.page, self.input.size))
        total_count = self.get_total_count()
        content_posts = self.__format__(content_posts)

        return Output(
            output_details={"data": content_posts, "total": total_count},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched posts(s)"
        )
