import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.state import manager


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_state():
    """Clean state before and after each test."""
    # Clear using the manager's actual data file
    data_file = manager.DATA_FILE
    if os.path.exists(data_file):
        os.remove(data_file)
    yield
    if os.path.exists(data_file):
        os.remove(data_file)
