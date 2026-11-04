import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from jose import jwt

from app.config import settings

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Proverava lozinku naspram bcrypt hash-a."""
    password_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """Generiše bcrypt hash iz lozinke."""
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    shop_id: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Kreira JWT token sa sub, shop_id, role."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "shop_id": str(shop_id),
        "role": role,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)