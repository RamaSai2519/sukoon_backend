from models.common import Common
from models.constants import OutputStatus
from models.interfaces import GetCallsInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.today_query = Common.get_today_query()
        self.query = self.common.get_internal_exclude_query(input.internal)

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

    def _get_calls_list(self) -> dict:
        calls = self.common.get_calls(
            query=self.query,
            page=int(self.input.page), size=int(self.input.size)
        )
        return {"data": calls}

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
