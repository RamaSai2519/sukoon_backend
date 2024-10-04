import json
from bson import ObjectId
from datetime import datetime
from models.common import Common
from helpers.base import call_graphql
from models.constants import OutputStatus
from models.admin_schedule import Schedule
from db.calls import get_schedules_collection
from helpers.schedule import ScheduleManager as sm
from models.interfaces import CreateScheduleInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.collection = get_schedules_collection()

    def prep_schedule(self) -> Schedule:
        schedule = Schedule(
            expert_id=self.input.expert,
            user_id=self.input.user,
            time=self.input.datetime,
            duration=self.input.duration,
            type=self.input.type
        )
        return schedule

    def schedule_call_job(self, document, schedule: Schedule) -> str:
        time = datetime.strptime(schedule.time, "%Y-%m-%dT%H:%M:%S.%fZ")
        record = self.collection.find_one(document, {"_id": 1})
        record_id = str(record["_id"]) if record else ""

        response = sm.scheduleCall(
            time, schedule.expert_id, schedule.user_id, record_id)

        return response

    def format_schedules(self, schedules):
        for schedule in schedules:
            schedule["requestMeta"] = json.loads(
                schedule.get("requestMeta", "{}"))

            expert_id = schedule["requestMeta"].get("expertId")
            schedule["expert"] = self.common.get_expert_name(
                ObjectId(expert_id)) if expert_id else None

            user_id = schedule["requestMeta"].get("userId")
            schedule["user"] = self.common.get_user_name(
                ObjectId(user_id)) if user_id else None

            schedule["datetime"] = schedule.get("scheduledJobTime")
        return {"data": schedules}

    def get_dynamo_schedules(self):
        query = """
            query MyQuery($limit: Int = 1000, $nextToken: String) {
                listScheduledJobs(limit: $limit, nextToken: $nextToken) {
                    nextToken
                    items {
                        id
                        status
                        isDeleted
                        requestMeta
                        scheduledJobTime
                        scheduledJobStatus
                    }
                }
            }
        """

        params = {"limit": 1000}
        all_items = []
        next_token = None

        while True:
            if next_token:
                params["nextToken"] = next_token
            else:
                params.pop("nextToken", None)

            response = call_graphql(
                query=query, params=params, message="get_scheduled_jobs")
            all_items.extend(response['listScheduledJobs']['items'])

            next_token = response['listScheduledJobs'].get('nextToken')
            if not next_token:
                break

        formatted_response = self.format_schedules(all_items)

        return formatted_response

    def compute(self) -> Output:
        if self.input.action == "create":
            schedule = self.prep_schedule()
            document = schedule.to_document()
            self.collection.insert_one(document)
            response = self.schedule_call_job(document, schedule)
        elif self.input.action == "delete":
            response = "Schedule deleted successfully"
            sm.cancelCall(self.input.scheduleId)
        elif self.input.action == "get":
            response = self.get_dynamo_schedules()

        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message="Data received successfully"
        )
