from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from models.constants import OutputStatus
from models.interfaces import Output
from configs import CONFIG as Config
import boto3
import uuid
import os


class Compute:
    def __init__(self, input) -> None:
        self.input: FileStorage = input['file']
        self.s3_client = boto3.client(
            "s3", region_name=Config.REGION, aws_access_key_id=Config.ACCESS_KEY,
            aws_secret_access_key=Config.SECRET_ACCESS_KEY
        )

    def compute(self) -> Output:
        print(self.input, 'file uploaded')
        story_id = str(uuid.uuid4())
        file_name = secure_filename(self.input.filename).replace(" ", "+")
        unique_filename = f"{int(os.times()[-1])}_{story_id}_{file_name}"

        metadata = {
            "fieldName": self.input.name.lower().replace(" ", "+")
        }

        self.s3_client.upload_fileobj(
            self.input,
            "sukoon-media",
            unique_filename,
            ExtraArgs={
                "Metadata": metadata,
                "ACL": "public-read",
                "ContentType": self.input.mimetype
            }
        )

        file_url = self.s3_client.meta.endpoint_url + "/sukoon-media/" + unique_filename

        return Output(
            output_details={"file_url": file_url},
            output_status=OutputStatus.SUCCESS,
            output_message="File uploaded successfully"
        )
