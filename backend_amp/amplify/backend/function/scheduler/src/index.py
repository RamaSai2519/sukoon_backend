import json
import controller
from .queries.scheduled_job import get_pending_scheduled_jobs, mark_my_job_as_picked

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
   try:
       print(f"Event: {event}")
       print(f"Context: {context}")

       time = event["time"]
       status = "PENDING"
       next_token = None
       first_time = True

       while next_token or first_time:
           data = get_pending_scheduled_jobs(
               time=time, status=status, nextToken=next_token
           )["scheduledJobsByStatusAndTime"]

           jobs = data["items"]
           for job in jobs:
               try:
                   if job.get("scheduledJobType"):
                       controller.process(job)
                   else:
                       print(f"no job type for given job {job}")
               except Exception as error:
                   print(
                       f"error in executing processor for job {job} with error {error}"
                   )
               if job.get("id"):
                   mark_my_job_as_picked(job.get("id", None))
           first_time = False
           next_token = data["nextToken"]

   except Exception as error:
       print(
           f"error in getting scheduled job for time {time} and status {status} error {error}"
       )
       return construct_response(statusCode=400, body={})
   return construct_response(statusCode=200, body={})