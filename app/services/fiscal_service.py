from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.fiscal_receipt import FiscalReceipt
from app.models.shop import Shop
from app.models.work_order import WorkOrder, WorkOrderItem


class FiscalService:
    """Servis za pripremu fiskalnih računa (simulacija PFR integracije)."""

    SANDBOX_URL = "https://vsdc.sandbox.suf.purs.gov.rs"
    PRODUCTION_URL = "https://vsdc.suf.purs.gov.rs"

    @classmethod
    def prepare_receipt_data(cls, db: Session, work_order: WorkOrder) -> Dict[str, Any]:
        """Priprema podatke za fiskalni račun iz radnog naloga."""
        shop = db.query(Shop).filter(Shop.id == work_order.shop_id).first()

        items = db.query(WorkOrderItem).filter(
            WorkOrderItem.work_order_id == work_order.id,
            WorkOrderItem.is_approved == True,
        ).all()

        if not items:
            raise ValueError("Nalog nema odobrenih stavki za fiskalizaciju.")

        receipt_items = []
        for item in items:
            receipt_items.append({
                "name": item.title,
                "quantity": float(item.quantity),
                "unit_price": float(item.unit_price),
                "total_price": float(item.quantity * item.unit_price),
                "tax_label": "Ђ",  # 20% PDV
            })

        total_amount = sum(i["total_price"] for i in receipt_items)
        tax_base = total_amount / Decimal("1.20")
        vat_amount = total_amount - tax_base

        return {
            "shop_name": shop.name if shop else "",
            "shop_pib": shop.pib or "" if shop else "",
            "shop_address": shop.address or "" if shop else "",
            "work_order_number": work_order.order_number,
            "items": receipt_items,
            "total_amount": float(total_amount),
            "tax_base": float(tax_base),
            "vat_amount": float(vat_amount),
            "vat_rate": 20.0,
        }

    @classmethod
    def create_fiscal_receipt(cls, db: Session, work_order: WorkOrder) -> FiscalReceipt:
        """Kreira zapis o fiskalnom računu (simulacija)."""
        data = cls.prepare_receipt_data(db, work_order)

        receipt_number = f"PFR-{work_order.order_number:06d}"
        verification_url = f"https://suf.purs.gov.rs/verify/{receipt_number}"

        receipt = FiscalReceipt(
            work_order_id=work_order.id,
            receipt_number=receipt_number,
            total_amount=Decimal(str(data["total_amount"])),
            tax_base=Decimal(str(data["tax_base"])),
            vat_amount=Decimal(str(data["vat_amount"])),
            vat_rate=Decimal("20.00"),
            pfr_status="PENDING",
            verification_url=verification_url,
            pfr_response=data,
        )
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return receipt

    @classmethod
    def get_receipt_for_order(cls, db: Session, work_order_id: UUID) -> Optional[FiscalReceipt]:
        """Vraća fiskalni račun za dati radni nalog."""
        return db.query(FiscalReceipt).filter(FiscalReceipt.work_order_id == work_order_id).first()