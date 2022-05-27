import json
import math
from requests.models import Response

from reports.core import schemas


class MockNBPApiResponse(Response):
    def __init__(self, status_code: int, value: int):
        super().__init__()
        self.status_code = status_code
        self.json_response = {
            "rates": [
                {
                    "bid": value
                }
            ]
        }
        self._content = json.dumps(self.json_response).encode()


def mock_convert_to_pln(amount: int, currency: schemas.Currency, *args):
    mock_exchange_rates = {
        "PLN": 1.0,
        "USD": 4.4031,
        "EUR": 4.6376,
        "GBP": 5.498
    }

    return math.floor(amount * mock_exchange_rates[currency])
