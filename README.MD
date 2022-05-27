# Transaction reports
Transaction reports REST API developed using [FastAPI](https://github.com/tiangolo/fastapi).
It provides the following endpoints:
- `/report` - Generates a report
- `/customer-report` - Generates a report for certain customer and saves it in the database
- `/customer-report/<customer_id:int>` - Retrieve last saved report for certain customer

Request contains lists of `PayByLink`, `DirectPayment` and `Card` objects with specified transaction dates in arbitrary timezone
and amounts in arbitrary currency.<br>
Report is a list of client's payments in chronological order, with payment data in uniform format (`PaymentInfo`).<br>
`PaymentInfo` has the following attributes:
- date - in the UTC time zone
- type - <i>card</i> / <i>pay_by_link</i> / <i>dp</i>
- payment_mean - e.g. <i>John Doe 510510******5100</i>
- description
- currency
- amount - in the original currency
- amount_in_pln - obtained with [NBP API](http://api.nbp.pl/en.html) using exchange rate from the transaction date.

## Installation
1. Run `pip install -r requirements.txt`.
2. From the root directory run `python3 reports/main.py`.
