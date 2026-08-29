from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import hashlib
import os
import hmac
import jwt
from passlib.context import CryptContext
from backend.app.core.config import settings

# Security Context using Argon2id with bcrypt and sha256 fallback
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt", "pbkdf2_sha256"],
    deprecated="auto"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback PBKDF2 SHA256 verification
        if hashed_password.startswith("pbkdf2$"):
            parts = hashed_password.split("$")
            if len(parts) == 3:
                salt, expected_hash = parts[1], parts[2]
                computed = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
                return hmac.compare_digest(computed, expected_hash)
        return False

def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception:
        # High-security standard PBKDF2 SHA256 fallback
        salt = os.urandom(16).hex()
        derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return f"pbkdf2${salt}${derived}"

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None, roles: Optional[list[str]] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "roles": roles or ["player"],
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
