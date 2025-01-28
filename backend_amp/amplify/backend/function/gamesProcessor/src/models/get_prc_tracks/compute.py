from shared.models.interfaces import GetPRCTracksInput as Input, Output
from shared.db.referral import get_prc_tracks_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.ref_tracks_collection = get_prc_tracks_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value
        )
        if self.input.filter_field in ['_id', 'user']:
            query = Common.get_filter_query(
                self.input.filter_field, self.input.filter_value, 'oid'
            )
        total = self.ref_tracks_collection.count_documents(query)
        if total <= 10:
            self.input.page = 1
            self.input.size = total
        cursor = self.ref_tracks_collection.find(query)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size)
        )
        data = Common.jsonify(list(paginated_cursor))

        return Output(
            output_details={
                'data': data,
                'total': total
            }
        )
