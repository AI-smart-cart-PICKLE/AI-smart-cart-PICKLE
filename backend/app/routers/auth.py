# app/routers/auth.py
from fastapi import APIRouter, Cookie, HTTPException
from app.utils.jwt import decode_token, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/refresh")
def refresh_access_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    new_access_token = create_access_token(payload["sub"])

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
