"""Admin authentication service."""

import bcrypt
from typing import Dict, Any
from backend.db.repositories.admin_repo import AdminRepository
from backend.auth.jwt_handler import JWTHandler


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


class AdminAuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return _hash_password(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return _verify_password(plain, hashed)

    @staticmethod
    async def login_admin(email: str, password: str) -> Dict[str, Any]:
        admin = await AdminRepository.get_admin_by_email(email)
        if not admin or not AdminAuthService.verify_password(password, admin["hashed_password"]):
            raise ValueError("Invalid admin credentials")

        await AdminRepository.update_last_login(admin["admin_id"])
        access_token = JWTHandler.create_access_token({"sub": admin["admin_id"], "role": "admin"})
        refresh_token = JWTHandler.create_refresh_token({"sub": admin["admin_id"], "role": "admin"})

        return {
            "admin_id": admin["admin_id"],
            "email": admin["email"],
            "full_name": admin["full_name"],
            "role": admin["role"],
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }