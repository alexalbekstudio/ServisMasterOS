from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ShopBase(BaseModel):
    name: str = Field(..., max_length=150)
    pib: Optional[str] = Field(None, max_length=20)
    maticni_broj: Optional[str] = Field(None, max_length=20)
    phone: str = Field(..., max_length=50)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field("Beograd", max_length=100)
    currency: Optional[str] = Field("RSD", max_length=10)
    sms_sender_name: Optional[str] = Field("SERVIS", max_length=11)
    bank_account: Optional[str] = Field(None, max_length=30)


class ShopCreate(ShopBase):
    pass


class ShopUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    pib: Optional[str] = Field(None, max_length=20)
    maticni_broj: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, max_length=10)
    sms_sender_name: Optional[str] = Field(None, max_length=11)
    bank_account: Optional[str] = Field(None, max_length=30)
    is_active: Optional[bool] = None


class ShopResponse(ShopBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)