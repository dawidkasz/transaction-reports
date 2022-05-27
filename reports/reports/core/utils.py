import datetime
import pytz
import math
import requests
from functools import lru_cache
from fastapi import status

from reports.core import schemas
from reports.core.exceptions import ExternalAPIError


def generate_report(request: schemas.ReportRequest) -> schemas.Report:
    """
    Generates a report containing payments in chronological order.
    """

    payments = []
    for payment in request.all_payments:
        date_utc = payment.created_at.astimezone(pytz.UTC)
        amount_in_pln = convert_to_pln(payment.amount, payment.currency, date_utc.date())

        payments.append(schemas.PaymentInfo(
            date=date_utc,
            type=payment.type_name,
            payment_mean=payment.payment_mean,
            description=payment.description,
            amount=payment.amount,
            currency=payment.currency,
            amount_in_pln=amount_in_pln
        ))

    payments.sort(key=lambda x: x.date)
    return schemas.Report(payments=payments)


@lru_cache(maxsize=256)
def get_currency_rate(currency: schemas.Currency, date: datetime.date) -> int:
    """
    Returns currency exchange rate(to PLN) from given date.
    """

    endpoint_url = f"http://api.nbp.pl/api/exchangerates/rates/C/{currency}"
    batch_size = datetime.timedelta(days=3)
    start_date = date - datetime.timedelta(days=2)
    end_date = date

    while True:
        if abs(date - start_date) > datetime.timedelta(days=14):
            raise ExternalAPIError(f"Can't find conversion "
                                   f"from {currency} - {date.isoformat()} to PLN.")

        url = f"{endpoint_url}/{start_date.isoformat()}/{end_date.isoformat()}/"
        response = requests.get(url)

        if response.status_code == status.HTTP_404_NOT_FOUND:
            start_date -= batch_size
            end_date -= datetime.timedelta(days=1)
            continue
        if not response.ok:
            raise ExternalAPIError(f"Error occured while converting "
                                   f"from {currency} - {date.isoformat()} to PLN.")

        response = response.json()
        return response["rates"][-1]["bid"]


def convert_to_pln(amount: int, currency: schemas.Currency, date: datetime.date) -> int:
    """
    Converts from other currency to PLN.
    """

    if currency == schemas.Currency.PLN:
        return amount

    latest_rate = get_currency_rate(currency, date)
    return math.floor(amount * latest_rate)
