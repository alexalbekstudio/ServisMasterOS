import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(120), nullable=True)
    is_company = Column(Boolean, default=False, nullable=True)
    company_name = Column(String(150), nullable=True)
    pib = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=True)

    __table_args__ = (
        Index("idx_customers_shop_phone", "shop_id", "phone"),
    )

    # Relacije
    shop = relationship("Shop", back_populates="customers")
    vehicles = relationship("Vehicle", back_populates="customer", cascade="all, delete-orphan")
    notifications = relationship("NotificationLog", back_populates="customer")