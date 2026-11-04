import uuid
import enum
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class InventoryChangeReason(str, enum.Enum):
    MANUAL_IN = "MANUAL_IN"
    WORK_ORDER_USED = "WORK_ORDER_USED"
    WORK_ORDER_RETURN = "WORK_ORDER_RETURN"
    CLIENT_REJECTED = "CLIENT_REJECTED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    CORRECTION = "CORRECTION"


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id", ondelete="CASCADE"), nullable=False)
    work_order_id = Column(UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_quantity = Column(Numeric(10, 2), nullable=False)
    previous_quantity = Column(Numeric(10, 2), nullable=False)
    new_quantity = Column(Numeric(10, 2), nullable=False)
    reason = Column(SQLEnum(InventoryChangeReason, name="inventory_change_reason"), nullable=False)
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

    part = relationship("Part")
    work_order = relationship("WorkOrder")
    user = relationship("User")