import uuid
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Part(Base):
    __tablename__ = "parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    sku = Column(String(50), nullable=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    purchase_price = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    selling_price = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    min_quantity = Column(Integer, default=2, nullable=False)

    shop = relationship("Shop")