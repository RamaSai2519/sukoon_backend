from bson import ObjectId
from shared.models.common import Common
from shared.db.experts import get_vacations_collection
from shared.models.interfaces import UpsertUserVacationInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_vacations_collection()

    def pop_immutable_fields(self, doc: dict) -> dict:
        fields = ['user', '_id', 'createdAt']
        for field in fields:
            doc.pop(field, None)
        return doc

    def prep_data(self, new_data: dict, old_data: dict = None) -> dict:
        if old_data:
            new_data = self.pop_immutable_fields(new_data)
            new_data = Common.merge_dicts(new_data, old_data)
        else:
            new_data['createdAt'] = Common.get_current_utc_time()
            new_data['isDeleted'] = False

        date_fields = ['createdAt', 'start_date', 'end_date']
        for field in date_fields:
            new_data[field] = Common.string_to_date(new_data, field)

        if 'user' in new_data and isinstance(new_data['user'], str):
            new_data['user'] = ObjectId(new_data['user'])

        new_data = Common.filter_none_values(new_data)
        return new_data

    def compute(self) -> Output:
        query = {'user': ObjectId(self.input.user)}
        doc = self.collection.find_one(query)
        if doc:
            doc = self.prep_data(self.input.__dict__, doc)
            self.collection.update_one(query, {'$set': doc})
            message = 'User vacation updated successfully'
        else:
            doc = self.prep_data(self.input.__dict__)
            self.collection.insert_one(doc)
            message = 'User vacation created successfully'

        return Output(
            output_details=Common.jsonify(doc),
            output_message=message
        )
