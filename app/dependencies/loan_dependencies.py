from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.services.loan_service import LoanService


def get_loan_or_404(loan_id: int, db: Session = Depends(get_db)):
    loan = LoanService.get_loan_by_id(db, loan_id)
    if loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado",
        )
    return loan
