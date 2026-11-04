from pydantic import BaseModel, EmailStr, Field


class ShopRegisterRequest(BaseModel):
    # Podaci o servisu
    shop_name: str = Field(..., max_length=150)
    shop_phone: str = Field(..., max_length=50)
    shop_address: str = Field(None, max_length=255)
    shop_city: str = Field("Beograd", max_length=100)

    # Podaci o vlasniku
    owner_name: str = Field(..., max_length=120)
    owner_email: EmailStr = Field(...)
    owner_password: str = Field(..., min_length=6, max_length=100)
    owner_phone: str = Field(None, max_length=50)