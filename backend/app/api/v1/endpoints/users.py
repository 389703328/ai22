from fastapi import APIRouter
from typing import List
from app.models.user import UserResponse, UserCreate

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users():
    return [
        UserResponse(id=1, username="testuser", email="test@example.com"),
        UserResponse(id=2, username="demo", email="demo@example.com"),
    ]


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    return UserResponse(id=3, username=user.username, email=user.email)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return UserResponse(id=user_id, username="testuser", email="test@example.com")
