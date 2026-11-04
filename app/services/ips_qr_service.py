import io
import base64
from decimal import Decimal
from typing import Optional

import qrcode

from app.models.shop import Shop
from app.models.work_order import WorkOrder
from app.models.vehicle import Vehicle


class IpsQrService:
    """Generiše NBS IPS QR kodove za plaćanje."""

    @staticmethod
    def generate_ips_payload(
        recipient_account: str,
        recipient_name: str,
        amount: Decimal,
        currency: str = "RSD",
        reference_number: Optional[str] = None,
        payment_purpose: str = "Usluga auto servisa",
    ) -> str:
        """Kreira string formatiran po NBS IPS standardu."""
        clean_acc = recipient_account.replace("-", "").replace(" ", "").strip()
        formatted_amount = f"{currency}{amount:.2f}".replace(".", ",")
        ref_block = f"|RO:{reference_number}" if reference_number else ""

        payload = (
            f"K:PR|V:01|C:1|"
            f"R:{clean_acc}|"
            f"N:{recipient_name[:70]}|"
            f"I:{formatted_amount}|"
            f"SF:289|"
            f"S:{payment_purpose[:35]}"
            f"{ref_block}"
        )
        return payload

    @classmethod
    def generate_base64_qr(cls, payload: str) -> str:
        """Generiše QR kod sliku u Base64 formatu spremnu za HTML <img>."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=2,
        )
        qr.add_data(payload)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

    @classmethod
    def get_order_payment_qr(
        cls, shop: Shop, work_order: WorkOrder, vehicle: Vehicle
    ) -> Optional[str]:
        """Kreira Base64 QR za dati radni nalog."""
        shop_acc = getattr(shop, "bank_account", None) or "160000000123456789"
        shop_title = shop.name or "Auto Centar"
        total = work_order.total_amount or Decimal("0.00")

        if total <= 0:
            return None

        ref_no = f"RN-{work_order.order_number}"
        purpose = f"Servis {vehicle.license_plate if vehicle else ''}"

        payload = cls.generate_ips_payload(
            recipient_account=shop_acc,
            recipient_name=shop_title,
            amount=total,
            currency="RSD",
            reference_number=ref_no,
            payment_purpose=purpose,
        )
        return cls.generate_base64_qr(payload)