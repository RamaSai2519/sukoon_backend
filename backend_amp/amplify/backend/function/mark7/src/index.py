from process_call_data import process_call_data
from config import db, calls_collection
from score_updater import updater
from notify import notify
from common import Common
from bson import ObjectId

class Mark7:
    def __init__(self, call: dict) -> None:
        self.call = self.format_call(call)

    def format_call(self, call: dict) -> dict:
        if "expert" in call:
            call["expert"] = ObjectId(call["expert"])
        if "user" in call:
            call["user"] = ObjectId(call["user"])
        call["initiatedTime"] = Common.string_to_date(call, "initiatedTime")
        return call

    def compute(self) -> None:
        duration = self.call.get("duration", "00:00:00")
        seconds = sum(
            int(x) * 60**i for i, x in enumerate(reversed(duration.split(":")))
        )
        if seconds > 120:
            print(f"call with duration {duration} longer than 2 minutes")
            if self.call.get("recording_url") not in ["None", ""]:
                print(f"Processing call {str(self.call['callId'])}")
                try:
                    user_document = db.users.find_one(
                        {"_id": self.call.get("user", "")})
                    expert_document = db.experts.find_one(
                        {"_id": self.call.get("expert", "")}
                    )
                    if not user_document or not expert_document:
                        return
                    user = user_document["name"]
                    expert = expert_document["name"]
                    user_calls = calls_collection.count_documents(
                        {"user": self.call["user"]})
                    notify(f"Processing call {str(self.call.get('callId'))} between {user} and {expert} on backup loop")
                    call_processed = process_call_data(
                        self.call, user, expert, user_document, expert_document, user_calls)
                    msg = "Call processed" if call_processed else "Call not processed"
                    print(msg)
                    updater(str(self.call["expert"]),
                            expert_document["phoneNumber"])
                except Exception as e:
                    error_message = f"An error occurred processing the call ({self.call.get('callId')}): {str(e)} on backup loop"
                    print(error_message)
                    notify(error_message)


def handler(event, context) -> dict:
    print(event)
    call = event.get("call", {})
    mark7 = Mark7(call)
    mark7.compute()
    return {"message": "Call is being processed"}