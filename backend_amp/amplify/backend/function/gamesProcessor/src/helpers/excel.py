import boto3
import pandas as pd
from io import BytesIO
from pytz import timezone
from datetime import datetime
from typing import List, Dict
from configs import CONFIG as Config


class ExcelS3Helper:
    def __init__(self, bucket_name: str = "sukoon-user-data") -> None:
        self.s3_client = boto3.client(
            "s3",
            region_name=Config.REGION,
            aws_access_key_id=Config.ACCESS_KEY,
            aws_secret_access_key=Config.SECRET_ACCESS_KEY
        )
        self.bucket_name = bucket_name

    def format_time(self, time_string: str) -> str:
        """Convert UTC time string to IST and format it."""
        try:
            utc_time = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
            ist_time = utc_time.astimezone(timezone('Asia/Kolkata'))
            return ist_time.strftime('%d %b %Y, %I:%M:%S %p')
        except Exception as e:
            return time_string

    def format_data(self, data: List[Dict]) -> List[Dict]:
        """Format fields based on their names and content."""
        formatted_data = []
        for item in data:
            formatted_item = {}
            for field_name, value in item.items():
                field_name_lower = field_name.lower()
                if any(keyword in field_name_lower for keyword in ['time', 'date', 'created', 'received', 'updated']):
                    formatted_item[field_name] = self.format_time(str(value))
                else:
                    formatted_item[field_name] = value
            formatted_data.append(formatted_item)
        return formatted_data

    def save_to_excel(self, data: List[Dict]) -> BytesIO:
        """Generate an Excel file from the provided data and return the file in memory."""
        df = pd.DataFrame(data)
        file_buffer = BytesIO()
        df.to_excel(file_buffer, index=False)
        file_buffer.seek(0)
        return file_buffer

    def delete_old_files(self, prefix: str, keep_latest: int = 1) -> None:
        """Delete all files with a given prefix except the latest `keep_latest` ones."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix)
            if 'Contents' not in response:
                print("No files found.")
                return

            files = sorted(
                response['Contents'], key=lambda x: x['LastModified'], reverse=True)
            for file in files[keep_latest:]:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name, Key=file['Key'])
                print(f"Deleted: {file['Key']}")

        except Exception as e:
            print(f"Error deleting files: {e}")

    def upload_to_s3(self, file_buffer: BytesIO, file_name: str) -> str:
        """Upload a file buffer to S3 and return the file URL."""
        endpoint_url = self.s3_client.meta.endpoint_url
        file_url = f"{endpoint_url}/{self.bucket_name}/{file_name}"
        metadata = {"fieldName": "excel_file"}

        self.s3_client.upload_fileobj(
            file_buffer,
            self.bucket_name,
            file_name,
            ExtraArgs={
                "Metadata": metadata,
                "ACL": "public-read",
                "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        )
        return file_url

    def create_and_upload_excel(self, file_name: str, data: List[Dict]) -> str:
        """Format data, create an Excel file, upload to S3, and return the S3 file URL."""
        formatted_data = self.format_data(data)
        file_buffer = self.save_to_excel(formatted_data)
        url = self.upload_to_s3(file_buffer, file_name)
        self.delete_old_files('engagement_data_', keep_latest=1)
        return url

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


# Example usage 1
# uploader = ExcelS3Helper()
# data = [{"timeCreated": "2024-01-01T10:00:00.000Z", "timeSpent": 120}]
# url = uploader.create_and_upload_excel('example.xlsx', data)
# print(url)

# Usage example 2
# file_finder = ExcelS3Helper()
# url = file_finder.get_latest_file_url('engagement_data_')
# print(url)
