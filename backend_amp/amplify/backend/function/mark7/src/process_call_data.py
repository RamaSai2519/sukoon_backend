from process_call_recording import process_call_recording
from upload_transcript import upload_transcript
from config import callsmeta_collection, calls_collection, users_collection
from datetime import datetime
import pytz


def process_call_data(call, user, expert, user_document, expert_document, user_calls):
    customer_persona = user_document.get("Customer Persona", "None")
    print(call, user, expert, customer_persona, user_calls, "process_call_data")

    (
        transcript,
        summary,
        conversation_score,
        conversation_score_details,
        saarthi_feedback,
        customer_persona,
        user_callback,
        topics,
    ) = process_call_recording(call, user, expert, customer_persona, user_calls)

    if not transcript or not customer_persona:
        return False

    transcript_url = upload_transcript(transcript, call["callId"])

    update_query = {"_id": user_document["_id"]}
    update_values = {"$set": {"Customer Persona": customer_persona}}
    users_collection.update_one(update_query, update_values)

    update_values = {
        "callId": call["callId"],
        "user": user_document["_id"],
        "expert": str(expert_document["_id"]),
        "conversationScore": conversation_score,
        "Score Breakup": conversation_score_details,
        "Saarthi Feedback": saarthi_feedback,
        "User Callback": user_callback,
        "Topics": topics,
        "Summary": summary,
        "transcript_url": transcript_url,
        "updatedAt": datetime.now(pytz.utc),
    }

    if callsmeta_collection.find_one({"callId": call["callId"]}):
        callsmeta_collection.update_one(
            {"callId": call["callId"]},
            {"$set": update_values},
        )
    else:
        update_values["createdAt"] = datetime.now(pytz.utc)
        callsmeta_collection.insert_one(
            update_values,
        )

    calls_collection.update_one(
        {"callId": call["callId"]},
        {"$set": {"conversationScore": conversation_score}},
    )
    return True
