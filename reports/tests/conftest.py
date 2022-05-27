import pytest
import pytz
from datetime import datetime
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, drop_database

from reports.core.database import Base
from reports.core.dependencies import get_db
from reports.app import app
from reports.core.schemas import Currency


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session", autouse=True)
def setup():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)

    yield

    if database_exists(SQLALCHEMY_DATABASE_URL):
        drop_database(SQLALCHEMY_DATABASE_URL)


@pytest.fixture(scope="session")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def request_data():
    return {
        "pay_by_link": [
            {
                "created_at": datetime(2022, 4, 5, 16, tzinfo=pytz.UTC),
                "currency": Currency.USD,
                "description": "Gym membership",
                "amount": 1284,
                "bank": "mbank",
            },
            {
                "created_at": datetime.fromisoformat("2021-10-10T12:00:00-05:00"),
                "currency": Currency.PLN,
                "amount": 99999,
                "bank": "pekao",
            }
        ],
        "dp": [
            {
                "created_at": datetime(2022, 5, 9, 8, tzinfo=pytz.UTC),
                "currency": Currency.GBP,
                "amount": 99,
                "iban": "DE91100000000123456789",
            }
        ],
        "card": [
            {
                "created_at": datetime.fromisoformat("2022-04-05T16:30:00+08:00"),
                "currency": Currency.EUR,
                "amount": 35422,
                "description": "Plane ticket",
                "cardholder_name": "John",
                "cardholder_surname": "Doe",
                "card_number": "5105105105105100"
            },
            {
                "created_at": datetime(2021, 3, 3, 21, 15, tzinfo=pytz.UTC),
                "currency": Currency.GBP,
                "amount": 2944,
                "cardholder_name": "John",
                "cardholder_surname": "Smith",
                "card_number": "5105105105105100"
            }
        ]
    }


@pytest.fixture
def simple_request_data():
    return {
        "pay_by_link": [
            {
                "created_at": "2021-12-13T01:01:43-08:00",
                "currency": "EUR",
                "amount": 3000,
                "description": "Gym membership",
                "bank": "mbank"
            }
        ]
    }
