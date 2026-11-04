from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class FiscalReceiptResponse(BaseModel):
    id: UUID
    work_order_id: UUID
    receipt_number: str
    total_amount: Decimal
    tax_base: Decimal
    vat_amount: Decimal
    vat_rate: Decimal
    pfr_status: str
    verification_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)