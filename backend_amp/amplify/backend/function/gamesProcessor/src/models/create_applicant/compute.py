from shared.models.interfaces import ApplicantInput as Input, Output
from shared.db.events import get_become_saarthis_collection
from shared.models.constants import OutputStatus
from shared.models.common import Common
from dataclasses import asdict


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.become_saarthis_collection = get_become_saarthis_collection()

    def insert_applicant(self) -> None:
        applicant_dict = asdict(self.input)
        applicant_dict.pop("_id")
        inserted_id = self.become_saarthis_collection.insert_one(
            applicant_dict).inserted_id
        self.input._id = inserted_id

    def validate_phone_number(self) -> bool:
        query = {"phoneNumber": self.input.phoneNumber}
        if self.input.slug:
            query["slug"] = self.input.slug
        if self.become_saarthis_collection.find_one(query):
            return False
        return True

    def prep_output(self) -> dict:
        data = asdict(self.input)
        return Common.jsonify(data)

    def compute(self) -> Output:
        if not self.validate_phone_number():
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message="Applicant already exists"
            )
        self.insert_applicant()
        output_details = self.prep_output()

        return Output(
            output_details=output_details,
            output_message="Applicant registered successfully"
        )
