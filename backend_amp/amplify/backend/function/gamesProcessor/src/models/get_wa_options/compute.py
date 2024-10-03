from models.common import Common
from db.users import get_user_collection
from models.constants import OutputStatus
from db.events import get_events_collection
from db.whatsapp import get_whatsapp_templates_collection
from models.interfaces import WaOptionsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.events_collection = get_events_collection()
        self.templates_collection = get_whatsapp_templates_collection()

    def get_user_cities(self) -> list:
        return list(self.users_collection.distinct("city"))

    def get_templates(self) -> list:
        templates = list(self.templates_collection.find())
        templates = [Common.jsonify(t) for t in templates]
        return templates

    def get_slugs(self) -> list:
        slugs = list(self.events_collection.find({}, {"slug": 1}))
        slugs = [Common.jsonify(s) for s in slugs]
        return slugs

    def compute(self) -> Output:
        cities = self.get_user_cities()
        templates = self.get_templates()
        slugs = self.get_slugs()

        final_data = {"cities": cities, "templates": templates, "slugs": slugs}

        return Output(
            output_details=final_data,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched data"
        )
