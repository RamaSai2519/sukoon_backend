import os
import json
import pytest
from flask.testing import FlaskClient
from shared.models.common import Common
from shared.db.users import get_user_collection
from shared.db.experts import get_experts_collections


def load_test_cases() -> list:
    test_cases = []
    for file_name in [
        'test_cases.json',
        # 'wa_cases.json'
    ]:
        with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
            test_cases.extend(json.load(f))
    return test_cases


class TestAPIs:
    def get_user_id(self) -> str:
        self.users_collection = get_user_collection()
        query = {'phoneNumber': '9936142128'}
        user = self.users_collection.find_one(query)
        if user is None:
            user = {
                'phoneNumber': '9936142128',
                'name': 'Mayank Dwivedi'
            }
            insertion = self.users_collection.insert_one(user)
            user['_id'] = insertion.inserted_id
        return str(user['_id'])

    def get_expert_id(self) -> str:
        self.experts_collection = get_experts_collections()
        query = {'phoneNumber': '9398036558'}
        expert = self.experts_collection.find_one(query)
        return str(expert['_id'])

    def get_user_token(self, expert_id: str, user_id: str) -> str:
        common = Common()
        balance = common.get_balance_type(expert_id)
        token = Common.get_token(user_id, balance)
        return token

    @pytest.fixture(autouse=True)
    def setup(self, client: FlaskClient) -> None:
        self.client = client

    @pytest.mark.parametrize("test_case", load_test_cases())
    def test_api(self, test_case) -> None:
        method = test_case['method']
        path = test_case['path']
        params = test_case.get('params', {})
        payload = test_case.get('payload', {})
        headers = test_case.get('headers', {})

        if path == '/actions/call' and method == 'POST':
            user_id = self.get_user_id()
            expert_id = self.get_expert_id()
            payload['user_id'] = user_id
            payload['expert_id'] = expert_id
            token = self.get_user_token(expert_id, user_id)
            headers['Authorization'] = f'Bearer {token}'

        if method == 'GET':
            response = self.client.get(
                path, query_string=params, headers=headers)
        elif method == 'POST':
            response = self.client.post(path, json=payload, headers=headers)
        else:
            pytest.fail(f"Unsupported method: {method}")

        print(response.json['output_message'])
        assert response.status_code == 200
