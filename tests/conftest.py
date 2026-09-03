import os
from pathlib import Path

TEST_DB = Path(__file__).parent / "test_devices.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["QUEUE_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)
