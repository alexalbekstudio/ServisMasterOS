from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    full_name: str = Field(..., max_length=150)
    phone: str = Field(..., max_length=50)
    email: Optional[EmailStr] = None
    is_company: Optional[bool] = False
    company_name: Optional[str] = Field(None, max_length=150)
    pib: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    is_company: Optional[bool] = None
    company_name: Optional[str] = Field(None, max_length=150)
    pib: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: UUID
    shop_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)