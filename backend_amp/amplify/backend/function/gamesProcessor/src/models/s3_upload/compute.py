from shared.models.interfaces import UploadInput as Input, Output
from shared.models.constants import OutputStatus
from shared.configs import CONFIG as config
import boto3


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.s3_client = boto3.client(
            "s3", region_name=config.REGION, aws_access_key_id=config.ACCESS_KEY,
            aws_secret_access_key=config.SECRET_ACCESS_KEY
        )

    def compute(self) -> Output:
        filename = self.input.file_name
        presigned_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': 'sukoon-media', 'Key': filename,
                    'ContentType': self.input.file_type},
            ExpiresIn=3600
        )

        return Output(
            output_details={"url": presigned_url},
            output_status=OutputStatus.SUCCESS,
            output_message="File uploaded successfully"
        )
