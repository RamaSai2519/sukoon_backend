import boto3
import requests
from io import BytesIO
from shared.configs import CONFIG as config
from shared.models.constants import OutputStatus
from shared.db.content import get_content_posts_collection
from shared.models.interfaces import Output, SaveContentInput as Input


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_content_posts_collection()
        self.s3_client = boto3.client(
            "s3",
            region_name=config.REGION,
            aws_access_key_id=config.ACCESS_KEY,
            aws_secret_access_key=config.SECRET_ACCESS_KEY
        )

    def prep_data(self) -> dict:
        photo = self.input.photo.__dict__
        photo["s3_url"] = self.download_and_upload_photo_to_s3()
        photo["unsplash_url"] = photo.pop("url")
        content = self.input.content.__dict__
        content["photo"] = photo
        return content

    def save_content(self, data: dict) -> None:
        inserted_id = self.collection.insert_one(data).inserted_id
        data["_id"] = str(inserted_id)
        return data

    def compute(self) -> Output:
        data = self.prep_data()
        saved_data = self.save_content(data)

        return Output(
            output_details=saved_data,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully saved content"
        )

    def download_and_upload_photo_to_s3(self) -> str:
        bucket_name = "sukoon-media"
        photo_url = self.input.photo.url
        file_name = self.input.photo.slug
        endpoint_url = self.s3_client.meta.endpoint_url
        file_url = f"{endpoint_url}/{bucket_name}/{file_name}"

        response = requests.get(photo_url)

        metadata = {"fieldName": "photo"}
        file_object = BytesIO(response.content)

        upload = self.s3_client.upload_fileobj(
            file_object,
            bucket_name,
            file_name,
            ExtraArgs={
                "Metadata": metadata,
                "ACL": "public-read",
                "ContentType": "image/jpeg"
            }
        )
        print(upload, "upload")

        return file_url
