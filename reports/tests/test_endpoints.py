import pytest
from fastapi import status

from reports.core import utils
from tests.mocking import MockNBPApiResponse, mock_convert_to_pln


@pytest.mark.parametrize("endpoint", ["report", "customer-report"])
def test_report_endpoints(monkeypatch, client, endpoint):
    monkeypatch.setattr(utils, 'convert_to_pln', mock_convert_to_pln)

    data = {
            "pay_by_link": [
                {
                    "created_at": "2021-05-13T01:01:43-08:00",
                    "currency": "EUR",
                    "amount": 3000,
                    "description": "Gym membership",
                    "bank": "mbank"
                }
            ],
            "dp": [],
            "card": [
                {
                    "created_at": "2021-05-13T09:00:05+02:00",
                    "currency": "PLN",
                    "amount": 2450,
                    "description": "REF123457",
                    "cardholder_name": "John",
                    "cardholder_surname": "Doe",
                    "card_number": "5105105105105100"
                }
            ]
    }

    if endpoint == "customer-report":
        data["customer_id"] = 10

    response = client.post(
        f"/{endpoint}",
        json=data
    )

    assert response.status_code == status.HTTP_200_OK

    response = response.json()

    assert response[0]['date'] == "2021-05-13T07:00:05+00:00"
    assert response[0]['payment_mean'] == "John Doe 510510******5100"

    assert response[1]['date'] == "2021-05-13T09:01:43+00:00"
    assert response[1]['amount_in_pln'] == 13912


@pytest.mark.parametrize("endpoint", ["report", "customer-report"])
def test_report_endpoints_external_api_failed(monkeypatch, client,
                                              endpoint, simple_request_data):
    monkeypatch.setattr(utils.requests, 'get',
                        lambda _: MockNBPApiResponse(status.HTTP_400_BAD_REQUEST, None))

    if endpoint == "customer-report":
        simple_request_data["customer_id"] = 5

    response = client.post(
        f"/{endpoint}",
        json=simple_request_data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("endpoint", ["report", "customer-report"])
def test_report_invalid_date(monkeypatch, client, endpoint, simple_request_data):
    monkeypatch.setattr(utils, 'convert_to_pln', mock_convert_to_pln)
    simple_request_data["pay_by_link"][0]["created_at"] = "2021-13-13T01:01:43-08:00"

    if endpoint == "customer-report":
        simple_request_data["customer_id"] = 5

    response = client.post(
        f"/{endpoint}",
        json=simple_request_data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("endpoint", ["report", "customer-report"])
def test_report_missing_required_field(monkeypatch, client, endpoint, simple_request_data):
    monkeypatch.setattr(utils, 'convert_to_pln', mock_convert_to_pln)
    simple_request_data["pay_by_link"][0].pop("bank")

    if endpoint == "customer-report":
        simple_request_data["customer_id"] = 5

    response = client.post(
        f"/{endpoint}",
        json=simple_request_data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_report_returns_latest(monkeypatch, client):
    monkeypatch.setattr(utils, 'convert_to_pln', mock_convert_to_pln)

    data1 = {
        "customer_id": 17,
        "dp": [
            {
                "created_at": "2022-01-07T14:30:00Z",
                "currency": "PLN",
                "amount": 500,
                "iban": "PL012345678901234",
            }
        ]
    }

    data2 = {
        "customer_id": 17,
        "dp": [
            {
                "created_at": "2022-01-07T15:30:00Z",
                "currency": "PLN",
                "amount": 900,
                "iban": "PL098765432109876",
            }
        ]
    }

    client.post(
        "/customer-report",
        json=data1
    )

    response = client.get("/customer-report/17")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["amount"] == 500

    client.post(
        "/customer-report",
        json=data2
    )

    response = client.get("/customer-report/17")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["amount"] == 900
