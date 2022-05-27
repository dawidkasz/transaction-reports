from sqlalchemy.orm import Session

from reports.core import models
from reports.core import schemas


def get_or_create_customer(db: Session, customer_id: int) -> models.Customer:
    db_customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id).first()
    if db_customer:
        return db_customer

    db_customer = models.Customer(id=customer_id)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def create_report(db: Session, customer_id: int, report: schemas.Report) -> models.Report:
    db_customer = get_or_create_customer(db, customer_id)

    db_report = models.Report(customer_id=db_customer.id)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    for payment in report.payments:
        db_payment = models.PaymentInfo(**payment.dict(), report_id=db_report.id)
        db.add(db_payment)

    db.commit()
    db.refresh(db_report)
    return db_report


def get_latest_customer_report(db: Session, customer_id: int) -> models.Report:
    query = db.query(models.Report).filter(
        models.Report.customer_id == customer_id).order_by(models.Report.id.desc())
    return query.first()
