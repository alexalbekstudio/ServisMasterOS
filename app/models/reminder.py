import uuid
from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, Text, ForeignKey, Index, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import ReminderType, ReminderStatus


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(ReminderType, name="reminder_type"), nullable=False)
    due_date = Column(Date, nullable=True)
    due_mileage = Column(Integer, nullable=True)
    status = Column(SQLEnum(ReminderStatus, name="reminder_status"), default=ReminderStatus.PENDING, nullable=True)
    scheduled_for = Column(Date, nullable=False)
    message_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=True)

    __table_args__ = (
        Index("idx_reminders_scheduled_status", "scheduled_for", "status"),
    )

    shop = relationship("Shop", back_populates="reminders")
    vehicle = relationship("Vehicle", back_populates="reminders")


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    recipient_phone = Column(String(50), nullable=False)
    channel = Column(String(20), default="SMS", nullable=True)
    message = Column(Text, nullable=False)
    gateway_message_id = Column(String(100), nullable=True)
    is_delivered = Column(Boolean, default=False, nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=True)

    shop = relationship("Shop", back_populates="notification_logs")
    customer = relationship("Customer", back_populates="notifications")