"""User authentication service."""

import bcrypt
from typing import Optional, Dict, Any
from backend.db.repositories.user_repo import UserRepository
from backend.auth.jwt_handler import JWTHandler
import logging

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    """Hash password using bcrypt directly (passlib incompatible with bcrypt 5.x)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    """Verify password using bcrypt directly."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


class UserAuthService:
    """Handle user registration and login."""

    @staticmethod
    def hash_password(password: str) -> str:
        return _hash_password(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return _verify_password(plain, hashed)

    @staticmethod
    async def register_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        if await UserRepository.user_exists_by_email(user_data["email"]):
            raise ValueError("Email already registered")
        if await UserRepository.user_exists_by_pan(user_data["pan_number"]):
            raise ValueError("PAN number already registered")

        user_data["hashed_password"] = UserAuthService.hash_password(user_data.pop("password"))
        user = await UserRepository.create_user(user_data)

        access_token = JWTHandler.create_access_token({"sub": user.user_id, "role": "user"})
        refresh_token = JWTHandler.create_refresh_token({"sub": user.user_id, "role": "user"})

        return {
            "user_id": user.user_id,
            "email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def login_user(email: str, password: str) -> Dict[str, Any]:
        user = await UserRepository.get_user_by_email(email)
        if not user or not UserAuthService.verify_password(password, user["hashed_password"]):
            raise ValueError("Invalid email or password")

        access_token = JWTHandler.create_access_token({"sub": user["user_id"], "role": "user"})
        refresh_token = JWTHandler.create_refresh_token({"sub": user["user_id"], "role": "user"})

        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }