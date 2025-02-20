from flask.testing import FlaskClient
import pytest


class TestExpertAPI:
    @pytest.fixture(autouse=True)
    def setup(self, client: FlaskClient) -> None:
        self.client = client

    def test_get_expert(self) -> None:
        response = self.client.get('/actions/expert')
        assert response.status_code == 200
        print(response.json['output_message'])

    def test_post_expert(self) -> None:
        payload = {
            "phoneNumber": "9398036558",
            "status": "offline",
            "name": "Sarathi Test",
            "isBusy": False
        }
        response = self.client.post('/actions/expert', json=payload)
        assert response.status_code == 200
        print(response.json['output_message'])
