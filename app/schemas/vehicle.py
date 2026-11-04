from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class VehicleBase(BaseModel):
    customer_id: UUID
    license_plate: str = Field(..., max_length=20)
    vin: Optional[str] = Field(None, max_length=17)
    make: str = Field(..., max_length=50)
    model: str = Field(..., max_length=50)
    year_of_manufacture: Optional[int] = Field(None, ge=1900, le=2100)
    engine_code: Optional[str] = Field(None, max_length=50)
    fuel_type: Optional[str] = Field(None, max_length=30)
    last_registered_at: Optional[date] = None
    current_mileage: Optional[int] = Field(0, ge=0)


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    customer_id: Optional[UUID] = None
    license_plate: Optional[str] = Field(None, max_length=20)
    vin: Optional[str] = Field(None, max_length=17)
    make: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    year_of_manufacture: Optional[int] = Field(None, ge=1900, le=2100)
    engine_code: Optional[str] = Field(None, max_length=50)
    fuel_type: Optional[str] = Field(None, max_length=30)
    last_registered_at: Optional[date] = None
    current_mileage: Optional[int] = Field(None, ge=0)


class VehicleResponse(VehicleBase):
    id: UUID
    shop_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)