import uuid
from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Shop(Base):
    __tablename__ = "shops"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    name = Column(String(150), nullable=False)
    pib = Column(String(20), nullable=True)
    maticni_broj = Column(String(20), nullable=True)
    phone = Column(String(50), nullable=False)
    email = Column(String(120), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), default="Beograd", nullable=True)
    currency = Column(String(10), default="RSD", nullable=True)
    sms_sender_name = Column(String(11), default="SERVIS", nullable=True)
    bank_account = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=True)

    # Relacije
    users = relationship("User", back_populates="shop", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="shop", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="shop", cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="shop", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="shop", cascade="all, delete-orphan")
    notification_logs = relationship("NotificationLog", back_populates="shop", cascade="all, delete-orphan")