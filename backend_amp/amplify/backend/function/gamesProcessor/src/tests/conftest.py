import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))

import pytest
from index import app
from typing import Any, Generator
from flask.testing import FlaskClient


@pytest.fixture
def client() -> Generator[FlaskClient, Any, None]:
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
