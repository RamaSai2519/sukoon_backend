from shared.models.common import Common
from shared.db.calls import get_calls_collection
from shared.models.interfaces import GetLeadsInput as Input, Output
from shared.db.users import get_user_collection, get_meta_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.meta_collection = get_meta_collection()
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()

    def __format__(self, user: dict) -> dict:
        query = {"user": user.get("_id")}
        user_meta: dict = self.meta_collection.find_one(query)
        if user_meta:
            user["leadSource"] = user_meta.get("source", "Website")
        else:
            user["leadSource"] = "Website"
        user.update(user_meta or {})
        return Common.jsonify(user)

    def get_leads(self, query: dict) -> dict:
        projection = {
            'name': 1, '_id': 1,
            'createdDate': 1, 'city': 1,
            'birthDate': 1, 'source': 1,
        }
        cursor = self.users_collection.find(query, projection).sort(
            self.input.sort_field, int(self.input.sort_order))
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size))
        users = list(paginated_cursor)
        return Output(
            output_details={
                'total': self.users_collection.count_documents(query),
                'data': [self.__format__(user) for user in users]
            })

    def get_call_users(self, number_of_calls: int) -> dict:
        pipeline = [
            {"$match": {"status": "successful"}},
            {"$group": {"_id": "$user", "call_count": {"$sum": 1}}},
            {"$match": {"call_count": 0}},
            {"$group": {
                "_id": "data",
                "unique_user_ids": {"$addToSet": "$_id"}
            }}
        ]
        if number_of_calls == 1:
            pipeline[2]['$match']['call_count'] = 1
        elif number_of_calls == 2:
            pipeline[2]['$match']['call_count'] = 2
        elif number_of_calls == 3:
            pipeline[2]['$match']['call_count'] = {"$gt": 2}
        data = list(self.calls_collection.aggregate(pipeline))
        users = data[0]['unique_user_ids']
        return {'_id': {'$in': users}}

    def prep_query(self) -> dict:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)
        if self.input.type == 'one_call_users':
            spec_query = self.get_call_users(1)
            query.update(spec_query)
            return query
        elif self.input.type == 'two_call_users':
            spec_query = self.get_call_users(2)
            query.update(spec_query)
            return query
        elif self.input.type == 'repeat_users':
            spec_query = self.get_call_users(3)
            query.update(spec_query)
            return query
        else:
            return query.update({'profileCompleted': False})

    def compute(self) -> dict:
        query = self.prep_query()
        return self.get_leads(query)
