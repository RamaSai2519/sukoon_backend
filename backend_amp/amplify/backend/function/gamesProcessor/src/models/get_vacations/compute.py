from shared.db.experts import get_vacations_collection, get_experts_collections
from shared.models.interfaces import GetVacationsInput as Input, Output
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.collection = get_vacations_collection()
        self.experts_collection = get_experts_collections()

    def __format__(self, doc: dict) -> dict:
        doc['user'] = self.common.get_expert_name(doc['user'])
        return Common.jsonify(doc)

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_value, self.input.filter_value
        )
        if self.input.filter_field == 'user':
            query = Common.get_filter_query(
                'name', self.input.filter_value
            )
            experts = self.experts_collection.distinct('_id', query)
            query['user'] = {'$in': experts}

        query['isDeleted'] = False if self.input.deleted == 'false' else True

        total = self.collection.count_documents(query)
        if total <= 10:
            self.input.page = 1
            self.input.size = total
        cursor = self.collection.find(query)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size)
        )
        data = [self.__format__(doc) for doc in list(paginated_cursor)]

        return Output(
            output_details={
                'data': data,
                'total': total
            },
            output_message="Successfully fetched vacation(s)"
        )
