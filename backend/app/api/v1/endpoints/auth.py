from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    return LoginResponse(access_token="fake_token", token_type="bearer")


@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}
