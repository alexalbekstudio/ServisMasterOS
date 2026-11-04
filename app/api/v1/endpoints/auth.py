from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.database import get_db
from app.models.enums import UserRole
from app.models.shop import Shop
from app.models.user import User
from app.schemas.auth import ShopRegisterRequest
from app.schemas.user import Token, UserResponse

router = APIRouter()


@router.post("/register-shop", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_shop(
    payload: ShopRegisterRequest,
    db: Session = Depends(get_db),
) -> Any:
    """Registruje novi servis i kreira vlasnički nalog (Role: OWNER)."""
    existing_user = db.query(User).filter(User.email == payload.owner_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Korisnik sa ovom email adresom već postoji.",
        )

    new_shop = Shop(
        name=payload.shop_name,
        phone=payload.shop_phone,
        address=payload.shop_address,
        city=payload.shop_city,
    )
    db.add(new_shop)
    db.flush()

    owner_user = User(
        shop_id=new_shop.id,
        email=payload.owner_email,
        password_hash=get_password_hash(payload.owner_password),
        full_name=payload.owner_name,
        phone=payload.owner_phone,
        role=UserRole.OWNER,
        is_active=True,
    )
    db.add(owner_user)
    db.commit()
    db.refresh(owner_user)
    return owner_user


@router.post("/login", response_model=Token)
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Any:
    """Standardna OAuth2 prijava sa email-om (username polje) i lozinkom."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pogrešan email ili lozinka.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Korisnički nalog je deaktiviran.",
        )

    shop = db.query(Shop).filter(Shop.id == user.shop_id).first()
    if not shop or not shop.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Servis je deaktiviran. Kontaktirajte podršku.",
        )

    access_token = create_access_token(
        subject=str(user.id),
        shop_id=str(user.shop_id),
        role=user.role.value if user.role else "MECHANIC",
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Vraća podatke o trenutno prijavljenom korisniku."""
    return current_user