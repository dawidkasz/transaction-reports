from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from reports.core import crud, schemas, utils
from reports.core.exceptions import ExternalAPIError
from reports.core.dependencies import get_db


router = APIRouter(tags=["reports"])


@router.post("/report", response_model=List[schemas.PaymentInfo])
async def create_report(request: schemas.ReportRequest):
    """
    Creates a report of the client's payments in chronological order.
    """

    try:
        report = utils.generate_report(request)
    except ExternalAPIError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    return report.payments


@router.post("/customer-report", response_model=List[schemas.PaymentInfo])
async def create_customer_report(request: schemas.CustomerReportRequest,
                                 db: Session = Depends(get_db)):
    """
    Creates a report of the client's payments in chronological order
    and saves it with respect to the particular customer.
    """

    try:
        report = utils.generate_report(request)
    except ExternalAPIError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    crud.create_report(db, request.customer_id, report)

    return report.payments


@router.get("/customer-report/{customer_id}", response_model=List[schemas.PaymentInfo])
async def get_customer_report(customer_id: int, db: Session = Depends(get_db)):
    """
    Retrieves last saved report for the particular customer.
    """

    report = crud.get_latest_customer_report(db, customer_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Report not found.")

    return report.payments
