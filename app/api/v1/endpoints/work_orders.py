from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_current_shop_id
from app.database import get_db
from app.models.customer import Customer
from app.models.enums import WorkOrderStatus
from app.models.inventory_log import InventoryChangeReason
from app.models.part import Part
from app.models.shop import Shop
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.work_order import (
    WorkOrder,
    WorkOrderItem,
    WorkOrderPhoto,
    WorkOrderStatusHistory,
)
from app.schemas.work_order import (
    PublicWorkOrderResponse,
    WorkOrderCreate,
    WorkOrderItemCreate,
    WorkOrderItemResponse,
    WorkOrderPhotoCreate,
    WorkOrderPhotoResponse,
    WorkOrderResponse,
    WorkOrderUpdate,
)
from app.services.ips_qr_service import IpsQrService
from app.services.notification_service import NotificationService
from app.services.pdf_service import PdfService

router = APIRouter()


class ClientApprovalRequest(BaseModel):
    item_id: UUID
    decision: bool


class ItemApprovalPayload(BaseModel):
    is_approved: bool


def recalculate_work_order_totals(work_order: WorkOrder, db: Session) -> None:
    """Preračunava total samo za odobrene stavke."""
    items = db.query(WorkOrderItem).filter(WorkOrderItem.work_order_id == work_order.id).all()
    labor_sum = Decimal("0.00")
    parts_sum = Decimal("0.00")

    for item in items:
        if item.requires_approval and item.is_approved is not True:
            continue
        item_total = Decimal(str(item.quantity)) * Decimal(str(item.unit_price))
        if item.is_part:
            parts_sum += item_total
        else:
            labor_sum += item_total

    work_order.total_labor = labor_sum
    work_order.total_parts = parts_sum
    work_order.total_amount = labor_sum + parts_sum
    db.commit()
    db.refresh(work_order)


@router.post("/", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
def create_work_order(
    payload: WorkOrderCreate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == payload.vehicle_id, Vehicle.shop_id == shop_id)
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vozilo nije pronađeno u vašem servisu.")

    if payload.mileage_at_reception > (vehicle.current_mileage or 0):
        vehicle.current_mileage = payload.mileage_at_reception

    last_order = (
        db.query(WorkOrder)
        .filter(WorkOrder.shop_id == shop_id)
        .order_by(WorkOrder.order_number.desc())
        .first()
    )
    next_number = (last_order.order_number + 1) if last_order else 1

    work_order = WorkOrder(
        shop_id=shop_id,
        vehicle_id=payload.vehicle_id,
        assigned_mechanic_id=payload.assigned_mechanic_id,
        order_number=next_number,
        mileage_at_reception=payload.mileage_at_reception,
        fuel_level=payload.fuel_level,
        complaint_description=payload.complaint_description,
        internal_notes=payload.internal_notes,
        status=WorkOrderStatus.RECEIVED,
    )
    db.add(work_order)
    db.commit()
    db.refresh(work_order)

    try:
        NotificationService.send_order_opened(db, work_order)
    except Exception as e:
        print(f"[Notifikacija] Greška: {e}")

    return work_order


@router.get("/", response_model=List[WorkOrderResponse])
def list_work_orders(
    status_filter: Optional[WorkOrderStatus] = Query(None, alias="status"),
    vehicle_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    query = db.query(WorkOrder).filter(WorkOrder.shop_id == shop_id)
    if status_filter:
        query = query.filter(WorkOrder.status == status_filter)
    if vehicle_id:
        query = query.filter(WorkOrder.vehicle_id == vehicle_id)
    return query.order_by(WorkOrder.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(
    work_order_id: UUID,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    work_order = (
        db.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id, WorkOrder.shop_id == shop_id)
        .first()
    )
    if not work_order:
        raise HTTPException(status_code=404, detail="Radni nalog nije pronađen.")
    return work_order


@router.patch("/{work_order_id}", response_model=WorkOrderResponse)
def update_work_order(
    work_order_id: UUID,
    payload: WorkOrderUpdate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    work_order = (
        db.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id, WorkOrder.shop_id == shop_id)
        .first()
    )
    if not work_order:
        raise HTTPException(status_code=404, detail="Radni nalog nije pronađen.")

    update_data = payload.model_dump(exclude_unset=True)
    old_status = work_order.status.value if work_order.status else None
    status_changed = False

    if "status" in update_data and update_data["status"]:
        new_status = update_data["status"]
        now = datetime.now(timezone.utc)
        if new_status == WorkOrderStatus.IN_PROGRESS and not work_order.started_at:
            work_order.started_at = now
        elif new_status == WorkOrderStatus.COMPLETED and not work_order.completed_at:
            work_order.completed_at = now
        elif new_status == WorkOrderStatus.DELIVERED and not work_order.delivered_at:
            work_order.delivered_at = now

        if old_status != new_status.value:
            status_changed = True
            history = WorkOrderStatusHistory(
                work_order_id=work_order.id,
                status=new_status,
                changed_by_user_id=current_user.id,
                note=update_data.get("internal_notes"),
            )
            db.add(history)

    for field, value in update_data.items():
        setattr(work_order, field, value)

    db.commit()
    db.refresh(work_order)

    if status_changed:
        try:
            NotificationService.send_status_change(
                db=db,
                work_order=work_order,
                old_status=old_status,
                new_status=work_order.status.value,
            )
        except Exception as e:
            print(f"[Status notifikacija greška]: {e}")

    return work_order


@router.post("/{work_order_id}/items", response_model=WorkOrderItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_work_order(
    work_order_id: UUID,
    payload: WorkOrderItemCreate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    from app.services.inventory_service import InventoryService

    work_order = (
        db.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id, WorkOrder.shop_id == shop_id)
        .first()
    )
    if not work_order:
        raise HTTPException(status_code=404, detail="Radni nalog nije pronađen.")

    inventory_part = None
    if payload.is_part:
        clean_title = payload.title.strip()
        inventory_part = (
            db.query(Part)
            .filter(Part.shop_id == shop_id, Part.name.ilike(clean_title))
            .first()
        )

    item = WorkOrderItem(
        work_order_id=work_order.id,
        is_part=payload.is_part,
        title=payload.title.strip(),
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        requires_approval=payload.requires_approval,
        inventory_item_id=inventory_part.id if inventory_part else None,
    )
    db.add(item)
    db.flush()

    if inventory_part and not payload.requires_approval:
        try:
            InventoryService.consume_item_from_stock(
                db=db, shop_id=shop_id, order_item=item, user_id=current_user.id,
            )
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    db.commit()
    db.refresh(item)
    recalculate_work_order_totals(work_order, db)

    if item.requires_approval:
        try:
            NotificationService.send_approval_request(db, work_order, item)
        except Exception as e:
            print(f"[Approval greška]: {e}")

    return item


@router.post("/{work_order_id}/photos", response_model=WorkOrderPhotoResponse, status_code=status.HTTP_201_CREATED)
def add_photo_to_work_order(
    work_order_id: UUID,
    payload: WorkOrderPhotoCreate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    work_order = (
        db.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id, WorkOrder.shop_id == shop_id)
        .first()
    )
    if not work_order:
        raise HTTPException(status_code=404, detail="Radni nalog nije pronađen.")

    photo = WorkOrderPhoto(
        work_order_id=work_order.id,
        category=payload.category,
        photo_url=payload.photo_url,
        description=payload.description,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.get("/{work_order_id}/pdf")
def download_work_order_pdf(
    work_order_id: UUID,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
):
    work_order = (
        db.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id, WorkOrder.shop_id == shop_id)
        .first()
    )
    if not work_order:
        raise HTTPException(status_code=404, detail="Radni nalog nije pronađen.")

    vehicle = db.query(Vehicle).filter(Vehicle.id == work_order.vehicle_id).first()
    customer = db.query(Customer).filter(Customer.id == vehicle.customer_id).first() if vehicle else None
    shop = db.query(Shop).filter(Shop.id == shop_id).first()

    if not vehicle or not customer or not shop:
        raise HTTPException(status_code=400, detail="Nedostaju podaci za PDF.")

    pdf_bytes = PdfService.generate_work_order_pdf(shop, work_order, vehicle, customer)
    filename = f"Radni_Nalog_{work_order.order_number}_{vehicle.license_plate}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )

@router.get("/{work_order_id}/pdf-en")
def download_work_order_pdf_en(
    work_order_id: UUID,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
):
    """Generiše PDF radni nalog na engleskom jeziku."""
    work_order = (
        db.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id, WorkOrder.shop_id == shop_id)
        .first()
    )
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found.")

    vehicle = db.query(Vehicle).filter(Vehicle.id == work_order.vehicle_id).first()
    customer = db.query(Customer).filter(Customer.id == vehicle.customer_id).first() if vehicle else None
    shop = db.query(Shop).filter(Shop.id == shop_id).first()

    if not vehicle or not customer or not shop:
        raise HTTPException(status_code=400, detail="Missing data.")

    pdf_bytes = PdfService.generate_work_order_pdf_en(shop, work_order, vehicle, customer)
    filename = f"WorkOrder_{work_order.order_number}_{vehicle.license_plate}_EN.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )

@router.get("/public/status/{tracking_token}", response_model=PublicWorkOrderResponse)
def get_public_work_order_status(
    tracking_token: str,
    db: Session = Depends(get_db),
) -> Any:
    work_order = db.query(WorkOrder).filter(WorkOrder.tracking_token == tracking_token).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Nevažeći link.")

    vehicle = db.query(Vehicle).filter(Vehicle.id == work_order.vehicle_id).first()
    shop = db.query(Shop).filter(Shop.id == work_order.shop_id).first()

    payment_qr = None
    if work_order.status in [WorkOrderStatus.COMPLETED, WorkOrderStatus.DELIVERED] and (work_order.total_amount or 0) > 0:
        if shop and vehicle:
            try:
                payment_qr = IpsQrService.get_order_payment_qr(shop, work_order, vehicle)
            except Exception:
                payment_qr = None

    return PublicWorkOrderResponse(
        order_number=work_order.order_number,
        tracking_token=work_order.tracking_token,
        status=work_order.status,
        vehicle_make=vehicle.make if vehicle else "Nepoznato",
        vehicle_model=vehicle.model if vehicle else "",
        vehicle_plate=vehicle.license_plate if vehicle else "",
        complaint_description=work_order.complaint_description,
        total_amount=work_order.total_amount or Decimal("0.00"),
        received_at=work_order.received_at,
        completed_at=work_order.completed_at,
        delivered_at=work_order.delivered_at,
        items=work_order.items,
        photos=work_order.photos,
        status_history=work_order.status_history,
        payment_qr_base64=payment_qr,
    )


@router.post("/public/approve/{tracking_token}")
def client_decision_on_item(
    tracking_token: str,
    payload: ClientApprovalRequest,
    db: Session = Depends(get_db),
):
    from app.services.inventory_service import InventoryService

    work_order = db.query(WorkOrder).filter(WorkOrder.tracking_token == tracking_token).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Radni nalog nije pronađen.")

    item = (
        db.query(WorkOrderItem)
        .filter(WorkOrderItem.id == payload.item_id, WorkOrderItem.work_order_id == work_order.id)
        .first()
    )
    if not item or not item.requires_approval:
        raise HTTPException(status_code=400, detail="Stavka ne postoji ili ne zahteva odobrenje.")

    item.is_approved = payload.decision
    item.approved_at = datetime.now(timezone.utc)

    if payload.decision is True and item.is_part and item.inventory_item_id:
        try:
            InventoryService.consume_item_from_stock(
                db=db, shop_id=work_order.shop_id, order_item=item, user_id=None,
            )
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    if payload.decision is False and item.is_part and item.inventory_item_id:
        InventoryService.return_item_to_stock(
            db=db, shop_id=work_order.shop_id, order_item=item,
            user_id=None, reason=InventoryChangeReason.CLIENT_REJECTED,
            note="Klijent odbio dodatni rad",
        )

    db.commit()
    recalculate_work_order_totals(work_order, db)

    return {
        "status": "success",
        "item_id": str(item.id),
        "is_approved": item.is_approved,
        "new_total": work_order.total_amount,
    }