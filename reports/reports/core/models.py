from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship

from reports.core.database import Base
from reports.core import schemas


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    reports = relationship("Report")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))

    payments = relationship("PaymentInfo")


class PaymentInfo(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))

    date = Column(DateTime)
    type = Column(Enum(schemas.PaymentType))
    payment_mean = Column(String(100))
    description = Column(Text, default="")
    amount = Column(Integer)
    currency = Column(Enum(schemas.Currency))
    amount_in_pln = Column(Integer)
