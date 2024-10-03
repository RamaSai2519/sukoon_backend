from process_call_data import process_call_data
from config import db, calls_collection
from score_updater import updater
from bson import ObjectId
from notify import notify
import datetime

class Mark7:
    def __init__(self, call: dict) -> None:
        self.call = call

    def compute(self) -> None:
        duration = self.call.get("duration", "00:00:00")
        seconds = sum(
            int(x) * 60**i for i, x in enumerate(reversed(duration.split(":")))
        )
        if seconds > 120:
            conScore = self.call["Conversation Score"] if "Conversation Score" in self.call else None
            if conScore is None and self.call.get("recording_url") not in ["None", ""]:
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
    return {"message": "Success"}

if __name__ == "__main__":
    call = {
        "_id": ObjectId("66f1427d155726d87e736a16"),
        "callId": "cf8e83da-2874-489b-bc39-e4955ff78680",
        "status": "successfull",
        "initiatedTime": datetime.datetime(2024, 9, 23, 10, 27, 9, 836000),
        "duration": "0:08:12",
        "transferDuration": "00:07:54",
        "recording_url": "https://sr.knowlarity.com/vr/fetchsound/?callid%3Dcf8e83da-2874-489b-bc39-e4955ff78680",
        "failedReason": "",
        "Conversation Score": None,
        "expert": ObjectId("6604694542f04a057fa2100f"),
        "profile": "",
        "user": ObjectId("6695140413812b454ec0e479"),
        "__v": 0
    }

    handler({"call": call}, None)
