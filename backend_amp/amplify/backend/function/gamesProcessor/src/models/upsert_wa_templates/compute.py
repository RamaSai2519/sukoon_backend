from dataclasses import asdict
from shared.models.common import Common
from shared.models.interfaces import Output
from shared.db.whatsapp import get_whatsapp_templates_collection
from shared.interfaces.whatsapp import UpsertWaTemplateInput as Input


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_whatsapp_templates_collection()

    def compute(self) -> Output:
        doc = asdict(self.input)
        doc = Common.convert_enums_to_values(doc)
        doc = Common.filter_none_values(doc)

        query = {"template_name": self.input.template_name}
        template = self.collection.find_one_and_update(
            filter=query,
            update={"$set": doc},
            upsert=True,
            return_document=True
        )

        return Output(
            output_details=Common.jsonify(template),
            output_message="Successfully upserted whatsapp template"
        )
