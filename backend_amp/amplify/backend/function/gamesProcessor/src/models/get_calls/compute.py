import threading
from datetime import datetime
from models.common import Common
from helpers.excel import ExcelS3Helper
from models.constants import OutputStatus
from models.interfaces import GetCallsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.query = self.prep_query()
        self.excel_helper = ExcelS3Helper()
        self.today_query = Common.get_today_query()

    def prep_query(self) -> dict:
        query = {}
        internal_query = self.common.get_internal_exclude_query(
            self.input.internal)

        if self.input.filter_field == 'expert':
            filter_query = self.common.get_filter_query(
                'name', self.input.filter_value)
            internal_query = self.common.get_internal_exclude_query(
                self.input.internal, '_id')
            query = {**filter_query, **internal_query}
            experts = list(self.common.experts_collection.find(query))
            expert_ids = [expert['_id'] for expert in experts]
            return {'expert': {'$in': expert_ids}}

        elif self.input.filter_field == 'user':
            filter_query = self.common.get_filter_query(
                'name', self.input.filter_value)
            users = list(self.common.users_collection.find(filter_query))
            user_ids = [user['_id'] for user in users]
            query = {'user': {'$in': user_ids}}

        elif self.input.filter_field == 'conversationScore':
            query = {self.input.filter_field: int(self.input.filter_value)}

        else:
            query = self.common.get_filter_query(
                self.input.filter_field, self.input.filter_value)

        return {**query, **internal_query}

    def _total_calls(self) -> int:
        return self.common.calls_collection.count_documents(self.query)

    def _get_home_calls(self) -> dict:
        query = {**self.query, **self.today_query}
        calls = self.common.get_calls(query=query)
        if len(calls) == 0:
            calls = self.common.get_calls(query=self.query, size=5)
        return {"data": calls}

    def _get_graph_calls(self) -> dict:
        calls = self.common.get_calls(req_names=False, query=self.query)
        return {"data": calls}

    def create_excel(self) -> str:
        calls = self.common.get_calls(query=self.query)
        time_string = self.common.current_time.strftime("%Y-%m-%d-%H-%M-%S")
        file_name = f"calls_data_{time_string}.xlsx"
        self.excel_helper.invoke_excel_helper(calls, file_name)

    def excel_url(self) -> str:
        prev_url = self.excel_helper.get_latest_file_url("engagement_data_")
        if not prev_url:
            threading.Thread(target=self.create_excel).start()
            return "Creating Excel File Now..."
        prev_file_time = prev_url.split("_")[-1].split(".")[0]
        prev_time = datetime.strptime(prev_file_time, "%Y-%m-%d-%H-%M-%S")
        time_diff = (self.common.current_time - prev_time).seconds
        if time_diff < 1800:
            diff = round((1800 - time_diff) / 60, 2)
            msg = f" and Next Excel File will be created in {diff} minutes"
            return prev_url, msg
        else:
            threading.Thread(target=self.create_excel).start()
            return prev_url, " and Creating Excel File Now..."

    def _get_calls_list(self) -> dict:
        calls = self.common.get_calls(
            query=self.query,
            page=int(self.input.page), size=int(self.input.size)
        )
        file_url, msg = self.excel_url()
        return {"data": calls, "fileUrl": file_url, "s3_msg": msg}

    def _get_call(self) -> dict:
        query = {"callId": self.input.callId}
        call = self.common.get_calls(query=query)
        if len(call) == 0:
            return {"data": None}
        else:
            call = call[0]

        call = self.common.populate_call_meta(call)
        call = self.common.jsonify(call)

        return {"data": call}

    def compute(self) -> Output:
        switcher = {
            "home": self._get_home_calls,
            "graph": self._get_graph_calls,
            "list": self._get_calls_list,
            "search": self._get_call
        }

        calls = switcher.get(self.input.dest)()
        calls["total"] = self._total_calls()

        if calls.get("data") is None:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="No Call Found"
            )

        return Output(
            output_details=calls,
            output_status=OutputStatus.SUCCESS,
            output_message="Fetched calls successfully"
        )
