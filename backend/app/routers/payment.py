from fastapi import APIRouter

router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_payments():
    return {"message": "Payment endpoint works"}
