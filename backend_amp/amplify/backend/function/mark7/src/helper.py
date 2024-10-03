from config import calls_collection, callsmeta_collection

calls = list(calls_collection.find(
    {"Conversation Score": {"$exists": True, "$eq": 0}}))

for call in calls:
    callmeta = callsmeta_collection.find_one({"callId": call["callId"]})
    if callmeta:
        calls_collection.update_one(
            {"callId": call["callId"]}, {"$set": {"Conversation Score": callmeta["Conversation Score"]}})
        print(
            f"Updated call {call['callId']} with Conversation Score {callmeta['Conversation Score']}")
