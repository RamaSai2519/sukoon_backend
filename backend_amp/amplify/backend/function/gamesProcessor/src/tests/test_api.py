import os
import json
import pytest
from flask.testing import FlaskClient


def load_test_cases() -> list:
    with open(os.path.join(os.path.dirname(__file__), 'test_cases.json')) as f:
        return json.load(f)


class TestAPIs:
    @pytest.fixture(autouse=True)
    def setup(self, client: FlaskClient) -> None:
        self.client = client

    @pytest.mark.parametrize("test_case", load_test_cases())
    def test_api(self, test_case) -> None:
        method = test_case['method']
        path = test_case['path']
        params = test_case.get('params', {})
        payload = test_case.get('payload', {})

        if method == 'GET':
            response = self.client.get(path, query_string=params)
        elif method == 'POST':
            response = self.client.post(path, json=payload)
        else:
            pytest.fail(f"Unsupported method: {method}")

        assert response.status_code == 200
        print(response.json['output_message'])

# TODO Add tests for:
# - /send_whatsapp