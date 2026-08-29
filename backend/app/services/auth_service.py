from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from backend.app.models.entities import User, Account, Profile
from backend.app.schemas.game_schemas import UserRegisterRequest, UserLoginRequest, TokenResponse
from backend.app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token

class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, req: UserRegisterRequest) -> TokenResponse:
        # Check existing user
        result = await db.execute(select(User).where((User.email == req.email) | (User.username == req.username)))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email is already registered."
            )
        
        # Create User
        new_user = User(
            email=req.email,
            username=req.username,
            hashed_password=get_password_hash(req.password),
            role="player"
        )
        db.add(new_user)
        await db.flush()

        # Create Account
        display_name = req.display_name or req.username
        new_account = Account(
            user_id=new_user.id,
            display_name=display_name
        )
        db.add(new_account)
        await db.flush()

        # Create Profile
        new_profile = Profile(
            account_id=new_account.id,
            level=1,
            credits=5000,
            fracture_shards=200
        )
        db.add(new_profile)
        await db.commit()
        await db.refresh(new_user)
        await db.refresh(new_profile)

        access_token = create_access_token(subject=new_user.id, roles=[new_user.role])
        refresh_token = create_refresh_token(subject=new_user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=new_user.id,
            username=new_user.username,
            profile_id=new_profile.id,
            role=new_user.role
        )

    @staticmethod
    async def authenticate_user(db: AsyncSession, req: UserLoginRequest) -> TokenResponse:
        result = await db.execute(select(User).where(User.username == req.username))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password credentials."
            )

        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been suspended by game moderation."
            )

        # Retrieve profile
        acc_res = await db.execute(select(Account).where(Account.user_id == user.id))
        account = acc_res.scalar_one_or_none()
        
        prof_res = await db.execute(select(Profile).where(Profile.account_id == account.id))
        profile = prof_res.scalar_one_or_none()

        access_token = create_access_token(subject=user.id, roles=[user.role])
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            username=user.username,
            profile_id=profile.id if profile else "",
            role=user.role
        )

    @staticmethod
    async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token."
            )

        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account no longer valid or is suspended."
            )

        acc_res = await db.execute(select(Account).where(Account.user_id == user.id))
        account = acc_res.scalar_one_or_none()
        prof_res = await db.execute(select(Profile).where(Profile.account_id == account.id))
        profile = prof_res.scalar_one_or_none()

        new_access = create_access_token(subject=user.id, roles=[user.role])
        new_refresh = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            user_id=user.id,
            username=user.username,
            profile_id=profile.id if profile else "",
            role=user.role
        )
