import uuid
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, UniqueConstraint, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    license_plate = Column(String(20), nullable=False)
    vin = Column(String(17), nullable=True)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year_of_manufacture = Column(Integer, nullable=True)
    engine_code = Column(String(50), nullable=True)
    fuel_type = Column(String(30), nullable=True)
    last_registered_at = Column(Date, nullable=True)
    current_mileage = Column(Integer, default=0, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=True)

    __table_args__ = (
        UniqueConstraint("shop_id", "license_plate", name="uq_vehicles_shop_license_plate"),
        Index("idx_vehicles_shop_plate", "shop_id", "license_plate"),
    )

    # Relacije
    shop = relationship("Shop", back_populates="vehicles")
    customer = relationship("Customer", back_populates="vehicles")
    work_orders = relationship("WorkOrder", back_populates="vehicle")
    reminders = relationship("Reminder", back_populates="vehicle", cascade="all, delete-orphan")