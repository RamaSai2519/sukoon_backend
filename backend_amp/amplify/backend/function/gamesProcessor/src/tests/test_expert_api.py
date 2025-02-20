from flask.testing import FlaskClient


def test_expert_api(client: FlaskClient) -> None:
    response = client.get('/actions/expert')
    assert response.status_code == 200
    assert response.json['output_status'] == 'SUCCESS'
