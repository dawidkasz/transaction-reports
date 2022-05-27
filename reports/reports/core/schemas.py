import datetime
import itertools
from enum import Enum
from typing import List, Iterable, Union, Optional
from pydantic import BaseModel
from pydantic.types import PaymentCardNumber


class Currency(str, Enum):
    PLN = "PLN"
    EUR = "EUR"
    GBP = "GBP"
    USD = "USD"


class PaymentType(str, Enum):
    PAY_BY_LINK = "pay_by_link"
    CARD = "card"
    DIRECT_PAYMENT = "dp"


class PaymentBase(BaseModel):
    created_at: datetime.datetime
    currency: Currency
    amount: int
    description: Optional[str] = ""


class PayByLink(PaymentBase):
    bank: str

    @property
    def payment_mean(self) -> str:
        return self.bank

    @property
    def type_name(self):
        return "pay_by_link"


class DirectPayment(PaymentBase):
    iban: str

    @property
    def payment_mean(self) -> str:
        return self.iban

    @property
    def type_name(self):
        return "dp"


class Card(PaymentBase):
    cardholder_name: str
    cardholder_surname: str
    card_number: PaymentCardNumber

    @property
    def cardholder_full_name(self) -> str:
        return f"{self.cardholder_name} {self.cardholder_surname}"

    @property
    def payment_mean(self) -> str:
        return f"{self.cardholder_full_name} {self.card_number.masked}"

    @property
    def type_name(self):
        return "card"


class PaymentInfo(BaseModel):
    date: datetime.datetime
    type: PaymentType
    payment_mean: str
    description: str
    amount: int
    currency: Currency
    amount_in_pln: int

    class Config:
        orm_mode = True


class ReportRequest(BaseModel):
    pay_by_link: Optional[List[PayByLink]] = []
    dp: Optional[List[DirectPayment]] = []
    card: Optional[List[Card]] = []

    @property
    def all_payments(self) -> Iterable[Union[PayByLink, DirectPayment, Card]]:
        return itertools.chain.from_iterable([
            self.pay_by_link,
            self.dp,
            self.card
        ])


class CustomerReportRequest(ReportRequest):
    customer_id: int


class Report(BaseModel):
    payments: List[PaymentInfo]

    class Config:
        orm_mode = True
