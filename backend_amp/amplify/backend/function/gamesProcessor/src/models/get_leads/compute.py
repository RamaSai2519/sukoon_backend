from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.models.interfaces import GetLeadsInput as Input, Output
from shared.db.users import get_user_collection, get_meta_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.meta_collection = get_meta_collection()
        self.users_collection = get_user_collection()
        #self.today_query= Common.get_today_query("CreatedDate")

    def get_user_query(self, leads: bool) -> dict:
        query = {"profileCompleted": not leads}
        if leads and self.input.filter_field and self.input.filter_value:
            query[self.input.filter_field] = {
                "$regex": self.input.filter_value, "$options": "i"}
        return query

    def __format__(self, user: dict) -> dict:
        query = {"user": user.get("_id")}
        user_meta: dict = self.meta_collection.find_one(query)
        user["leadSource"] = user_meta.get(
            "source", "Website") if user_meta else "Website"
        return Common.jsonify(user)

    def get_leads(self, query: dict) -> list:
        projection = {"customerPersona": 0}
        sort_order = self.input.sort_order if self.input.sort_order else -1
        sort_field = self.input.sort_field if self.input.sort_field else "createdDate"

        cursor = self.users_collection.find(query, projection)
        sorted_cursor = cursor.sort(sort_field, int(sort_order))

        page, size = int(self.input.page), int(self.input.size)
        user_leads = list(Common.paginate_cursor(sorted_cursor, page, size))
        return [self.__format__(user) for user in user_leads]

    def compute(self) -> Output:
        leads_query = self.get_user_query(leads=True)
        output_data = {}

        if self.input.data:
            leads = self.get_leads(leads_query)
            output_data["data"] = leads

        return Output(output_details=output_data)
