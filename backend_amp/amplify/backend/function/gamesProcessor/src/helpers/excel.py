import json
import boto3
from configs import CONFIG as config


class ExcelS3Helper:
    def __init__(self, bucket_name: str = "sukoon-user-data") -> None:
        self.s3_client = boto3.client(
            "s3",
            region_name=config.REGION,
            aws_access_key_id=config.ACCESS_KEY,
            aws_secret_access_key=config.SECRET_ACCESS_KEY
        )
        self.bucket_name = bucket_name

    def get_latest_file_url(self, prefix: str) -> str:
        """List files with a given prefix and return the public URL of the latest one."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix)
            if 'Contents' not in response:
                print("No files found.")
                return None

            files = sorted(
                response['Contents'], key=lambda x: x['LastModified'], reverse=True)
            latest_file = files[0]['Key']

            file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{latest_file}"
            return file_url

        except Exception as e:
            print(f"Error retrieving file: {e}")
            return None

    def invoke_excel_helper(self, data, file_name):
        client = boto3.client('lambda')
        response = client.invoke(
            FunctionName="excelUploader-main",
            InvocationType='RequestResponse',
            Payload=json.dumps({
                "data": data,
                "file_name": file_name
            })
        )
        response_payload = json.loads(response['Payload'].read())
        return response_payload
