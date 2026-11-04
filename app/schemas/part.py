from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PartBase(BaseModel):
    sku: Optional[str] = None
    name: str = Field(..., max_length=150)
    purchase_price: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    selling_price: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    quantity: int = Field(0, ge=0)
    min_quantity: int = Field(2, ge=0)


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    quantity: Optional[int] = None
    min_quantity: Optional[int] = None


class PartResponse(PartBase):
    id: UUID
    shop_id: UUID

    model_config = ConfigDict(from_attributes=True)