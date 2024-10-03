from datetime import datetime, date
from bson import ObjectId
import pytz


class Common:
    def __init__(self):
        pass

    @staticmethod
    def jsonify(doc: dict) -> dict:
        for field, value in doc.items():
            if isinstance(value, ObjectId):
                doc[field] = str(value)
            elif isinstance(value, datetime):
                if value.tzinfo is None:
                    value = value.replace(tzinfo=pytz.utc)
                doc[field] = value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return doc

    @staticmethod
    def string_to_date(doc: dict, field: str) -> date:
        if field in doc and doc[field] is not None and isinstance(doc[field], str):
            doc[field] = datetime.strptime(doc[field], "%Y-%m-%dT%H:%M:%S.%fZ")
        return doc[field]

    @staticmethod
    def duration_str_to_seconds(duration: str) -> int:
        duration = duration.split(":")
        hours, minutes, seconds = map(int, duration)
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def seconds_to_duration_str(seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        formatted_duration = []
        if hours > 0:
            formatted_duration.append(f"{int(hours)}h")

        if minutes > 0:
            formatted_duration.append(f"{int(minutes)}m")

        if seconds > 0:
            formatted_duration.append(f"{int(seconds)}s")

        return " ".join(formatted_duration) if formatted_duration else "0s"
