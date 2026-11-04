import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(120), nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(SQLEnum(UserRole, name="user_role"), default=UserRole.MECHANIC, nullable=True)
    theme_preference = Column(String(10), default="auto", nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=True)

    __table_args__ = (
        UniqueConstraint("shop_id", "email", name="uq_users_shop_email"),
    )

    # Relacije
    shop = relationship("Shop", back_populates="users")
    assigned_work_orders = relationship("WorkOrder", back_populates="assigned_mechanic")