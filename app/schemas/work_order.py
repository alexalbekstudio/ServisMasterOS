from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import WorkOrderStatus, PhotoCategory


class WorkOrderItemBase(BaseModel):
    is_part: bool = Field(False)
    title: str = Field(..., max_length=200)
    quantity: Decimal = Field(Decimal("1.00"), ge=Decimal("0.01"))
    unit_price: Decimal = Field(..., ge=Decimal("0.00"))
    requires_approval: bool = Field(False)


class WorkOrderItemCreate(WorkOrderItemBase):
    pass


class WorkOrderItemResponse(WorkOrderItemBase):
    id: UUID
    work_order_id: UUID
    total_price: Decimal
    is_approved: Optional[bool] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkOrderPhotoBase(BaseModel):
    category: PhotoCategory
    photo_url: str
    description: Optional[str] = Field(None, max_length=255)


class WorkOrderPhotoCreate(WorkOrderPhotoBase):
    pass


class WorkOrderPhotoResponse(WorkOrderPhotoBase):
    id: UUID
    work_order_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkOrderBase(BaseModel):
    vehicle_id: UUID
    assigned_mechanic_id: Optional[UUID] = None
    mileage_at_reception: int = Field(..., ge=0)
    fuel_level: Optional[str] = Field(None, max_length=20)
    complaint_description: str
    internal_notes: Optional[str] = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdate(BaseModel):
    assigned_mechanic_id: Optional[UUID] = None
    status: Optional[WorkOrderStatus] = None
    mileage_at_reception: Optional[int] = Field(None, ge=0)
    fuel_level: Optional[str] = Field(None, max_length=20)
    complaint_description: Optional[str] = None
    internal_notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class WorkOrderResponse(WorkOrderBase):
    id: UUID
    shop_id: UUID
    order_number: int
    tracking_token: str
    status: WorkOrderStatus
    total_labor: Decimal
    total_parts: Decimal
    total_amount: Decimal
    received_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[WorkOrderItemResponse] = []
    photos: List[WorkOrderPhotoResponse] = []

    model_config = ConfigDict(from_attributes=True)


class StatusHistoryItem(BaseModel):
    status: WorkOrderStatus
    created_at: datetime
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PublicWorkOrderResponse(BaseModel):
    order_number: int
    tracking_token: str
    status: WorkOrderStatus
    vehicle_make: str
    vehicle_model: str
    vehicle_plate: str
    complaint_description: Optional[str] = None
    total_amount: Decimal
    received_at: datetime
    completed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    items: List[WorkOrderItemResponse] = []
    photos: List[WorkOrderPhotoResponse] = []
    status_history: List[StatusHistoryItem] = []
    payment_qr_base64: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)