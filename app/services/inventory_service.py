from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.inventory_log import InventoryChangeReason, InventoryLog
from app.models.part import Part
from app.models.work_order import WorkOrder, WorkOrderItem, WorkOrderStatus


class InventoryService:

    @classmethod
    def record_stock_change(
        cls,
        db: Session,
        shop_id: UUID,
        part_id: UUID,
        delta: Decimal,
        reason: InventoryChangeReason,
        work_order_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        note: Optional[str] = None,
    ) -> Part:
        """Menja stanje artikla i upisuje neizbrisiv trag u inventory_logs."""
        part = (
            db.query(Part)
            .filter(Part.id == part_id, Part.shop_id == shop_id)
            .with_for_update()
            .first()
        )
        if not part:
            raise ValueError("Artikal nije pronađen u magacinu.")

        prev_qty = Decimal(str(part.quantity))
        delta_dec = Decimal(str(delta))
        new_qty = prev_qty + delta_dec

        if new_qty < 0:
            raise ValueError(
                f"Nedovoljno zaliha za deo {part.name}. "
                f"Raspoloživo: {prev_qty}, traženo smanjenje: {abs(delta_dec)}"
            )

        part.quantity = new_qty

        log_entry = InventoryLog(
            shop_id=shop_id,
            part_id=part.id,
            work_order_id=work_order_id,
            user_id=user_id,
            change_quantity=delta_dec,
            previous_quantity=prev_qty,
            new_quantity=new_qty,
            reason=reason,
            note=note,
        )
        db.add(log_entry)
        return part

    @classmethod
    def consume_item_from_stock(
        cls,
        db: Session,
        shop_id: UUID,
        order_item: WorkOrderItem,
        user_id: Optional[UUID] = None,
    ):
        """Troši deo sa lagera pri dodavanju na radni nalog."""
        if not order_item.is_part or not order_item.inventory_item_id:
            return

        qty_to_consume = -Decimal(str(order_item.quantity))  # negativno = izlaz
        cls.record_stock_change(
            db=db,
            shop_id=shop_id,
            part_id=order_item.inventory_item_id,
            delta=qty_to_consume,
            reason=InventoryChangeReason.WORK_ORDER_USED,
            work_order_id=order_item.work_order_id,
            user_id=user_id,
            note=f"Ugrađeno na nalog (stavka: {order_item.title})",
        )

    @classmethod
    def return_item_to_stock(
        cls,
        db: Session,
        shop_id: UUID,
        order_item: WorkOrderItem,
        user_id: Optional[UUID] = None,
        reason: InventoryChangeReason = InventoryChangeReason.WORK_ORDER_RETURN,
        note: Optional[str] = None,
    ):
        """Vraća pojedinačni ugrađeni deo nazad na stanje u magacin."""
        if not order_item.is_part or not order_item.inventory_item_id:
            return

        qty_to_return = Decimal(str(order_item.quantity))
        cls.record_stock_change(
            db=db,
            shop_id=shop_id,
            part_id=order_item.inventory_item_id,
            delta=qty_to_return,
            reason=reason,
            work_order_id=order_item.work_order_id,
            user_id=user_id,
            note=note or "Povrat sa radnog naloga",
        )

    @classmethod
    def cancel_work_order_and_restock(
        cls,
        db: Session,
        shop_id: UUID,
        work_order_id: UUID,
        user_id: Optional[UUID] = None,
        cancel_reason: str = "Storniranje naloga",
    ) -> WorkOrder:
        """Stornira radni nalog i vraća sve ugrađene delove u magacin."""
        order = (
            db.query(WorkOrder)
            .filter(WorkOrder.id == work_order_id, WorkOrder.shop_id == shop_id)
            .first()
        )
        if not order:
            raise ValueError("Radni nalog nije pronađen.")

        if order.status == WorkOrderStatus.CANCELLED:
            raise ValueError("Nalog je već storniran.")

        for item in order.items:
            if item.is_part and item.inventory_item_id:
                cls.return_item_to_stock(
                    db=db,
                    shop_id=shop_id,
                    order_item=item,
                    user_id=user_id,
                    reason=InventoryChangeReason.ORDER_CANCELLED,
                    note=f"Storniran nalog #{order.order_number}: {cancel_reason}",
                )

        order.status = WorkOrderStatus.CANCELLED
        db.commit()
        return order