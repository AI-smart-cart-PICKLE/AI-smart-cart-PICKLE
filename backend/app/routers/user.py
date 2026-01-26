from fastapi import APIRouter

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_users():
    return [{"username": "Test User", "email": "test@example.com"}]
