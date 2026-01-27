from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LedgerEntry

router = APIRouter(
    prefix="/api/ledger",
    tags=["ledger"],
)

@router.get("/")
def read_ledgers(
    db: Session = Depends(get_db),
):
    ledgers = db.query(LedgerEntry).limit(5).all()

    return [
        {
            "ledger_entry_id": l.ledger_entry_id,
            "amount": l.amount,
            "category": l.category,
            "memo": l.memo,
            "spend_date": l.spend_date,
        }
        for l in ledgers
    ]