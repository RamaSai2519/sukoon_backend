from models.interfaces import PhotosInput as Input, Output
from models.constants import OutputStatus
import requests


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.url = "https://api.unsplash.com/search/photos"

    def get_photos(self):
        pass

    def compute(self) -> Output:

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched expert(s)"
        )
