from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def setup_and_teardown():
    print("🧪 starting tests...")
    yield
    print("✅ finished!")
