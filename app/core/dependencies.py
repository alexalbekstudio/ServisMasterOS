from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

# OAuth2 scheme — čita token iz "Authorization: Bearer <token>" header-a
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Validira JWT token i vraća korisnika iz baze."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nevažeći autentifikacioni podaci",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        shop_id: str = payload.get("shop_id")
        role: str = payload.get("role")
        if user_id is None or shop_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Proverava da li je korisnički nalog aktivan."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Korisnički nalog je deaktiviran",
        )
    return current_user


def get_current_shop_id(
    current_user: User = Depends(get_current_active_user),
) -> UUID:
    """Vraća ID servisa trenutno ulogovanog korisnika (multi-tenant izolacija)."""
    return current_user.shop_id