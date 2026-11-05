from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_current_shop_id
from app.database import get_db
from app.models.inventory_log import InventoryChangeReason
from app.models.part import Part
from app.models.user import User
from app.schemas.part import PartCreate, PartResponse, PartUpdate
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.get("/", response_model=List[PartResponse])
def list_parts(
    search: Optional[str] = Query(None),
    low_stock_only: bool = Query(False),
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    query = db.query(Part).filter(Part.shop_id == shop_id)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter((Part.name.ilike(s)) | (Part.sku.ilike(s)))
    if low_stock_only:
        query = query.filter(Part.quantity <= Part.min_quantity)
    return query.order_by(Part.name.asc()).all()


@router.post("/", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
def create_part(
    payload: PartCreate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    clean_sku = payload.sku.strip() if payload.sku else None

    existing_part = None
    if clean_sku:
        existing_part = db.query(Part).filter(Part.shop_id == shop_id, Part.sku == clean_sku).first()

    if existing_part:
        if payload.selling_price > 0:
            existing_part.selling_price = payload.selling_price
        if payload.quantity > 0:
            InventoryService.record_stock_change(
                db=db, shop_id=shop_id, part_id=existing_part.id,
                delta=payload.quantity, reason=InventoryChangeReason.MANUAL_IN,
                user_id=current_user.id, note=f"Ručni unos (SKU: {clean_sku})",
            )
        db.commit()
        db.refresh(existing_part)
        return existing_part

    part = Part(
        shop_id=shop_id, sku=clean_sku, name=payload.name.strip(),
        purchase_price=payload.purchase_price, selling_price=payload.selling_price,
        quantity=0, min_quantity=payload.min_quantity,
    )
    db.add(part)
    db.flush()

    if payload.quantity > 0:
        InventoryService.record_stock_change(
            db=db, shop_id=shop_id, part_id=part.id,
            delta=payload.quantity, reason=InventoryChangeReason.MANUAL_IN,
            user_id=current_user.id, note=f"Početno stanje (SKU: {clean_sku})",
        )

    db.commit()
    db.refresh(part)
    return part


@router.patch("/{part_id}", response_model=PartResponse)
def update_part(
    part_id: UUID,
    payload: PartUpdate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    part = db.query(Part).filter(Part.id == part_id, Part.shop_id == shop_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Deo nije pronađen.")

    update_data = payload.model_dump(exclude_unset=True)

    if "quantity" in update_data and update_data["quantity"] is not None:
        new_qty = update_data["quantity"]
        delta = new_qty - part.quantity
        if delta != 0:
            InventoryService.record_stock_change(
                db=db, shop_id=shop_id, part_id=part.id,
                delta=delta, reason=InventoryChangeReason.CORRECTION,
                user_id=current_user.id, note="Ručna korekcija",
            )
        del update_data["quantity"]

    for field, val in update_data.items():
        setattr(part, field, val)

    db.commit()
    db.refresh(part)
    return part

@router.get("/export/csv")
def export_parts_csv(
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
):
    """Izvoz magacina u CSV format."""
    import csv
    import io
    from fastapi.responses import StreamingResponse

    parts = (
        db.query(Part)
        .filter(Part.shop_id == shop_id)
        .order_by(Part.name)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "SKU", "Naziv", "Prodajna cena (RSD)", "Količina", "Minimum"
    ])

    for p in parts:
        writer.writerow([
            p.sku or "",
            p.name or "",
            float(p.selling_price or 0),
            p.quantity or 0,
            p.min_quantity or 0,
        ])

    output.seek(0)
    content = "\ufeff" + output.getvalue()

    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="magacin.csv"'},
    )