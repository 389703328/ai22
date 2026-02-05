"""
User service for business logic
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.exceptions import NotFoundException, BadRequestException


class UserService:
    """Service for user business logic"""

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        """Create a new user with validation"""
        # Check if username already exists
        existing_user = await self.repo.get_by_username(user_create.username)
        if existing_user:
            raise BadRequestException("Username already exists")

        # Check if email already exists
        existing_email = await self.repo.get_by_email(user_create.email)
        if existing_email:
            raise BadRequestException("Email already exists")

        user = await self.repo.create(user_create)
        return UserResponse.model_validate(user)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Get user by ID"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return UserResponse.model_validate(user)

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username"""
        user = await self.repo.get_by_username(username)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def get_all_users(
        self, skip: int = 0, limit: int = 100
    ) -> List[UserResponse]:
        """Get all users with pagination"""
        users = await self.repo.get_all(skip, limit)
        return [UserResponse.model_validate(user) for user in users]

    async def update_user(self, user_id: int, user_update: UserUpdate) -> UserResponse:
        """Update user with validation"""
        # Check if user exists
        existing_user = await self.repo.get_by_id(user_id)
        if not existing_user:
            raise NotFoundException("User not found")

        # Check username uniqueness if being updated
        if user_update.username and user_update.username != existing_user.username:
            username_exists = await self.repo.get_by_username(user_update.username)
            if username_exists:
                raise BadRequestException("Username already exists")

        # Check email uniqueness if being updated
        if user_update.email and user_update.email != existing_user.email:
            email_exists = await self.repo.get_by_email(user_update.email)
            if email_exists:
                raise BadRequestException("Email already exists")

        user = await self.repo.update(user_id, user_update)
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        return await self.repo.delete(user_id)
