from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_current_shop_id
from app.database import get_db
from app.models.user import User
from app.models.work_order import WorkOrder
from app.services.fiscal_service import FiscalService

router = APIRouter()


class FiscalizeRequest(BaseModel):
    work_order_id: UUID


@router.post("/receipt", response_model=Dict[str, Any])
def create_fiscal_receipt(
    payload: FiscalizeRequest,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    work_order = db.query(WorkOrder).filter(
        WorkOrder.id == payload.work_order_id, WorkOrder.shop_id == shop_id
    ).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Radni nalog nije pronađen.")

    if work_order.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Nalog mora biti završen pre fiskalizacije.")

    existing = FiscalService.get_receipt_for_order(db, work_order.id)
    if existing:
        return {
            "success": True,
            "message": "Fiskalni račun već postoji.",
            "receipt": {
                "receipt_number": existing.receipt_number,
                "total_amount": float(existing.total_amount),
                "verification_url": existing.verification_url,
            },
        }

    try:
        receipt = FiscalService.create_fiscal_receipt(db, work_order)
        return {
            "success": True,
            "message": "Fiskalni račun je kreiran (simulacija).",
            "receipt": {
                "receipt_number": receipt.receipt_number,
                "total_amount": float(receipt.total_amount),
                "tax_base": float(receipt.tax_base),
                "vat_amount": float(receipt.vat_amount),
                "verification_url": receipt.verification_url,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/receipt/{work_order_id}", response_model=Dict[str, Any])
def get_fiscal_receipt(
    work_order_id: UUID,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    receipt = FiscalService.get_receipt_for_order(db, work_order_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Fiskalni račun nije pronađen.")

    return {
        "receipt_number": receipt.receipt_number,
        "total_amount": float(receipt.total_amount),
        "tax_base": float(receipt.tax_base),
        "vat_amount": float(receipt.vat_amount),
        "verification_url": receipt.verification_url,
        "created_at": receipt.created_at.isoformat() if receipt.created_at else None,
    }