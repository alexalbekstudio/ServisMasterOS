import uuid
import secrets
from sqlalchemy import (
    Column, String, Integer, Numeric, Text, Boolean, DateTime,
    ForeignKey, Index, Computed, text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import WorkOrderStatus, PhotoCategory


def generate_tracking_token() -> str:
    return secrets.token_hex(32)


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False)
    assigned_mechanic_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    order_number = Column(Integer, nullable=False)
    tracking_token = Column(String(64), unique=True, nullable=False, default=generate_tracking_token)
    status = Column(SQLEnum(WorkOrderStatus, name="work_order_status"), default=WorkOrderStatus.RECEIVED, nullable=True)
    mileage_at_reception = Column(Integer, nullable=False)
    fuel_level = Column(String(20), nullable=True)
    complaint_description = Column(Text, nullable=False)
    internal_notes = Column(Text, nullable=True)
    total_labor = Column(Numeric(12, 2), default=0.00, nullable=True)
    total_parts = Column(Numeric(12, 2), default=0.00, nullable=True)
    total_amount = Column(Numeric(12, 2), default=0.00, nullable=True)
    received_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=True)

    __table_args__ = (
        Index("idx_work_orders_tracking_token", "tracking_token"),
        Index("idx_work_orders_shop_status", "shop_id", "status"),
    )

    # Relacije
    shop = relationship("Shop", back_populates="work_orders")
    vehicle = relationship("Vehicle", back_populates="work_orders")
    assigned_mechanic = relationship("User", back_populates="assigned_work_orders")
    items = relationship("WorkOrderItem", back_populates="work_order", cascade="all, delete-orphan")
    photos = relationship("WorkOrderPhoto", back_populates="work_order", cascade="all, delete-orphan")
    status_history = relationship(
        "WorkOrderStatusHistory",
        back_populates="work_order",
        cascade="all, delete-orphan",
        order_by="WorkOrderStatusHistory.created_at",
    )
    fiscal_receipt = relationship("FiscalReceipt", back_populates="work_order", uselist=False, cascade="all, delete-orphan")


class WorkOrderItem(Base):
    __tablename__ = "work_order_items"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    work_order_id = Column(UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False)
    is_part = Column(Boolean, default=False, nullable=True)
    title = Column(String(255), nullable=False)
    quantity = Column(Numeric(8, 2), default=1.00, nullable=True)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(12, 2), Computed("quantity * unit_price", persisted=True), nullable=True)
    requires_approval = Column(Boolean, default=False, nullable=False)
    is_approved = Column(Boolean, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("parts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=True)

    work_order = relationship("WorkOrder", back_populates="items")
    inventory_item = relationship("Part", foreign_keys=[inventory_item_id])


class WorkOrderPhoto(Base):
    __tablename__ = "work_order_photos"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    work_order_id = Column(UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False)
    category = Column(SQLEnum(PhotoCategory, name="photo_category"), nullable=False)
    photo_url = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=True)

    work_order = relationship("WorkOrder", back_populates="photos")


class WorkOrderStatusHistory(Base):
    __tablename__ = "work_order_status_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    work_order_id = Column(UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum(WorkOrderStatus, name="work_order_status"), nullable=False)
    changed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

    work_order = relationship("WorkOrder", back_populates="status_history")
    changed_by = relationship("User")