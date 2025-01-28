from shared.models.interfaces import GetBlogPostsInput as Input, Output
from shared.db.content import get_blogposts_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.collection = get_blogposts_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value
        )
        if self.input.filter_field == "tags":
            query = Common.get_filter_query(
                self.input.filter_field, self.input.filter_value, 'list')

        total = self.collection.count_documents(query)
        if total <= 10:
            self.input.page = 1
            self.input.size = total
        cursor = self.collection.find(query)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size)
        )
        data = Common.jsonify(list(paginated_cursor))

        return Output(
            output_details={
                'data': data,
                'total': total
            },
            output_message="Fetched Docs",
        )
