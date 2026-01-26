from fastapi import APIRouter

router = APIRouter(
    prefix="/api/carts",
    tags=["carts"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_carts():
    return {"message": "Cart endpoint works"}
