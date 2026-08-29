from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.schemas.game_schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, RefreshTokenRequest
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.register_user(db, req)

@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.authenticate_user(db, req)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.refresh_tokens(db, req.refresh_token)

@router.post("/logout")
async def logout():
    return {"status": "success", "message": "Successfully logged out session."}
