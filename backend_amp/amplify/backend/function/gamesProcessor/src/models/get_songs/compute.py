from shared.models.common import Common
from shared.db.content import get_songs_collection
from shared.models.interfaces import GetSongsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_songs_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value
        )
        if self.input.filter_field == 'user_id':
            query = Common.get_filter_query(
                self.input.filter_field, self.input.filter_value, 'oid'
            )

        total = self.collection.count_documents(query)
        if total <= 10:
            self.input.page = 1
            self.input.size = total

        cursor = self.collection.find(query)
        cursor = Common.paginate_cursor(cursor, int(
            self.input.page), int(self.input.size))
        songs = Common.jsonify(list(cursor))

        return Output(
            output_details={
                'data': songs,
                'total': total
            },
            output_message="Successfully fetched song(s)"
        )
