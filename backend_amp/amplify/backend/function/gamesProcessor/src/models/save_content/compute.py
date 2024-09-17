from models.interfaces import SaveContentInput as Input, Output
from db.content import get_content_posts_collection
from models.constants import OutputStatus


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_content_posts_collection()

    def compute(self) -> Output:


        return Output(
            output_details="content",
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully saved content"
        )
