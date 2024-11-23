from shared.models.interfaces import GetApplicantsInput as Input, Output
from shared.models.constants import OutputStatus, indianLanguages
from shared.db.events import get_become_saarthis_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.become_saarthis_collection = get_become_saarthis_collection()

    def __format__(self, spec: list) -> list:
        for s in spec:
            s["workingHours"] = Common.array_to_string(
                s["workingHours"]) if "workingHours" in s else ""
            if "languages" in s:
                languages = s["languages"]
                final_languages = [indianLanguage["value"]
                                   for language in languages for indianLanguage in indianLanguages if indianLanguage["key"] == language]
                s["languages"] = Common.array_to_string(final_languages)
            s = Common.jsonify(s)
        return spec

    def compute(self) -> Output:
        query = {'formType': self.input.formType}
        cursor = self.become_saarthis_collection.find(
            query).sort("createdDate", -1)
        paginated_cursor = Common.paginate_cursor(
            cursor, int(self.input.page), int(self.input.size))
        data = self.__format__(list(paginated_cursor))
        total_count = self.become_saarthis_collection.count_documents(query)

        return Output(
            output_status=OutputStatus.SUCCESS,
            output_message="Data fetched successfully",
            output_details={"data": data, "total": total_count}
        )
