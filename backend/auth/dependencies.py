"""FastAPI route dependencies for authentication."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.auth.jwt_handler import JWTHandler
from backend.db.repositories.user_repo import UserRepository
from backend.db.repositories.admin_repo import AdminRepository

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = JWTHandler.verify_token(token)
    if not payload or payload.get("role") != "user":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token")
    user = await UserRepository.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = JWTHandler.verify_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")
    admin = await AdminRepository.get_admin_by_id(payload["sub"])
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin