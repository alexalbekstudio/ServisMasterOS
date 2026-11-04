import uuid
import enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class SubscriptionPlan(str, enum.Enum):
    BASIC = "BASIC"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    TRIAL = "TRIAL"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, unique=True)
    plan = Column(SQLEnum(SubscriptionPlan, name="subscription_plan"), default=SubscriptionPlan.BASIC, nullable=False)
    status = Column(SQLEnum(SubscriptionStatus, name="subscription_status"), default=SubscriptionStatus.TRIAL, nullable=False)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    current_period_start = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    max_users = Column(Integer, default=1, nullable=False)
    max_work_orders_per_month = Column(Integer, default=50, nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)

    shop = relationship("Shop", back_populates="subscription")