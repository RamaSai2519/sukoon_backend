from datetime import datetime, date
from bson import ObjectId


def string_to_date(doc: dict, field: str) -> date:
    if field in doc:
        doc[field] = datetime.strptime(doc[field], "%Y-%m-%dT%H:%M:%S.%fZ")
    return doc[field]


def jsonify(doc: dict) -> dict:
    for field, value in doc.items():
        if isinstance(value, ObjectId):
            doc[field] = str(value)
        elif isinstance(value, datetime):
            doc[field] = datetime.strftime(value, "%Y-%m-%dT%H:%M:%S")
    return doc
