"""Authentication routes for user and admin."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.auth.user_auth import UserAuthService
from backend.auth.admin_auth import AdminAuthService
from backend.utils.response import APIResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str
    pan_number: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register_user(request: UserRegisterRequest):
    try:
        result = await UserAuthService.register_user(request.dict())
        return APIResponse.success(data=result, message="Registration successful")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login_user(request: LoginRequest):
    try:
        result = await UserAuthService.login_user(request.email, request.password)
        return APIResponse.success(data=result, message="Login successful")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/admin/login")
async def login_admin(request: LoginRequest):
    try:
        result = await AdminAuthService.login_admin(request.email, request.password)
        return APIResponse.success(data=result, message="Admin login successful")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))