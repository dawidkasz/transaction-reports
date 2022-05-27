import datetime
import pytz
import pytest
from fastapi import status

from reports.core import utils
from reports.core.schemas import (
    Currency, PayByLink, DirectPayment,
    Card, ReportRequest
)
from reports.core.exceptions import ExternalAPIError
from tests.mocking import MockNBPApiResponse, mock_convert_to_pln


def test_convert_to_pln_foreign_currency(monkeypatch):
    monkeypatch.setattr(utils.requests, 'get',
                        lambda _: MockNBPApiResponse(status.HTTP_200_OK, 3.7421))

    assert utils.convert_to_pln(1100, Currency.USD, datetime.date(2021, 10, 10)) == 4116


def test_convert_to_pln_pln(monkeypatch):
    monkeypatch.setattr(utils.requests, 'get',
                        lambda _: MockNBPApiResponse(status.HTTP_200_OK, 3.7421))

    assert utils.convert_to_pln(99253, Currency.PLN, datetime.date(2021, 10, 10)) == 99253


def test_convert_to_pln_invalid_response(monkeypatch):
    monkeypatch.setattr(utils.requests, 'get',
                        lambda _: MockNBPApiResponse(status.HTTP_400_BAD_REQUEST, None))

    with pytest.raises(ExternalAPIError):
        utils.convert_to_pln(1, Currency.GBP, datetime.date(2022, 2, 1))


def test_generate_report(monkeypatch, request_data):
    monkeypatch.setattr(utils, 'convert_to_pln', mock_convert_to_pln)

    request = ReportRequest(
        pay_by_link=[PayByLink(**item) for item in request_data["pay_by_link"]],
        dp=[DirectPayment(**item) for item in request_data["dp"]],
        card=[Card(**item) for item in request_data["card"]]
    )

    report_payments = utils.generate_report(request).payments

    assert report_payments[0].date == datetime.datetime(2021, 3, 3, 21, 15,
                                                        tzinfo=pytz.UTC)
    assert report_payments[0].amount_in_pln == 16186
    assert report_payments[0].type == "card"
    assert report_payments[0].payment_mean == "John Smith 510510******5100"

    assert report_payments[1].date == datetime.datetime(2021, 10, 10, 17, tzinfo=pytz.UTC)
    assert report_payments[1].amount_in_pln == report_payments[1].amount
    assert report_payments[1].type == "pay_by_link"

    assert report_payments[2].type == "card"
    assert report_payments[2].payment_mean == "John Doe 510510******5100"
    assert report_payments[2].description == "Plane ticket"

    assert report_payments[3].date == datetime.datetime(2022, 4, 5, 16, tzinfo=pytz.UTC)
    assert report_payments[3].payment_mean == "mbank"
    assert report_payments[3].currency == Currency.USD

    assert report_payments[4].payment_mean == "DE91100000000123456789"
    assert report_payments[4].type == "dp"
    assert report_payments[4].amount_in_pln == 544
