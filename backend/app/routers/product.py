from fastapi import APIRouter

router = APIRouter(
    prefix="/api/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_products():
    return [{"name": "Test Product", "price": 1000}]
