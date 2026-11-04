from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ReminderType, ReminderStatus


class ReminderBase(BaseModel):
    vehicle_id: UUID
    type: ReminderType
    due_date: Optional[date] = None
    due_mileage: Optional[int] = Field(None, ge=0)
    scheduled_for: date
    message_text: Optional[str] = None


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(BaseModel):
    due_date: Optional[date] = None
    due_mileage: Optional[int] = Field(None, ge=0)
    scheduled_for: Optional[date] = None
    status: Optional[ReminderStatus] = None
    message_text: Optional[str] = None


class ReminderResponse(ReminderBase):
    id: UUID
    shop_id: UUID
    status: ReminderStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationLogResponse(BaseModel):
    id: UUID
    shop_id: UUID
    customer_id: Optional[UUID] = None
    recipient_phone: str
    channel: str
    message: str
    gateway_message_id: Optional[str] = None
    is_delivered: bool
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)