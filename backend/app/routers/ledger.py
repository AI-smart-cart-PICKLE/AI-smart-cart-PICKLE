#가계부 관련 API
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/ledgers",
    tags=["ledgers"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_ledgers():
    return {"message": "Ledger endpoint works"}