from models.interfaces import PhotosInput as Input, Output
from models.constants import OutputStatus
from configs import CONFIG as Config
import requests


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.access_key = Config.UNSPLASH_API_KEY
        self.url = "https://api.unsplash.com/search/photos"

    def fetch_photos(self) -> dict:
        headers = {'Authorization': f'Client-ID {self.access_key}'}
        params = {
            'query': self.input.query,
            'per_page': self.input.per_page,
            'page': self.input.page
        }
        response = requests.get(self.url, headers=headers, params=params)
        return response.json()

    def __format__(self, photos: list) -> list:
        for photo in photos:
            photo['url'] = photo['urls']['raw']
            photo['url'] = str(photo['url']).split('?')[0]
        return photos

    def compute(self) -> Output:
        photos = self.fetch_photos()
        formatted_photos = self.__format__(photos.get('results', []))

        return Output(
            output_details=formatted_photos,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched photo(s)"
        )
