from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.db.referral import get_offers_collection
from shared.models.interfaces import ListOffersInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.input.page = int(self.input.page)
        self.input.size = int(self.input.size)
        self.offers_collection = get_offers_collection()

    def prep_query(self):
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)
        query["validTill"] = {"$gte": Common.get_current_time()}

        if self.input.include_expired == "true":
            query.pop("validTill", None)

        return query

    def compute(self) -> Output:
        query = self.prep_query()
        cursor = self.offers_collection.find(query)
        cursor = Common.paginate_cursor(
            cursor, self.input.page, self.input.size)
        data = [Common.jsonify(doc) for doc in list(cursor)]

        total = self.offers_collection.count_documents(query)
        final_data = {
            "data": data,
            "total": total,
            "page": self.input.page,
            "size": self.input.size
        }

        return Output(
            output_details=final_data,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched data"
        )
