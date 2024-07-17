import json
import controller


def construct_response(statusCode, body):
    response = {
        "statusCode": statusCode,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps(body),
    }
    return response


def handler(event, context):
    print(f"Event: {event}")
    print(f"Context: {context}")
    
    records = event["Records"]
    for record in records:
        print(f"Record: {record}")
        if record["eventName"] != "INSERT":
            responseBody = {
               "message": "Processing only for newly created records."
            }
            continue
        else:
            controller.process(record["dynamodb"]["NewImage"])

    return construct_response(statusCode=201, body={})