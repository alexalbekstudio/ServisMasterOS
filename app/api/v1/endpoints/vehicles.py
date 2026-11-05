from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_shop_id
from app.database import get_db
from app.models.enums import WorkOrderStatus
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder, WorkOrderItem
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate

router = APIRouter()


@router.get("/", response_model=List[VehicleResponse])
def search_vehicles(
    plate: Optional[str] = Query(None, description="Pretraga po tablici"),
    customer_id: Optional[UUID] = Query(None, description="Filter po vlasniku"),
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    """Pretraga postojećih vozila u bazi servisa."""
    query = db.query(Vehicle).filter(Vehicle.shop_id == shop_id)
    if plate:
        clean_plate = plate.upper().replace("-", "").replace(" ", "").strip()
        query = query.filter(Vehicle.license_plate.ilike(f"%{clean_plate}%"))
    if customer_id:
        query = query.filter(Vehicle.customer_id == customer_id)
    return query.limit(20).all()


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    """Unos novog vozila za dati servis."""
    clean_plate = payload.license_plate.upper().replace("-", "").replace(" ", "").strip()

    existing = (
        db.query(Vehicle)
        .filter(Vehicle.shop_id == shop_id, Vehicle.license_plate == clean_plate)
        .first()
    )
    if existing:
        return existing

    vehicle = Vehicle(
        shop_id=shop_id,
        customer_id=payload.customer_id,
        license_plate=clean_plate,
        make=payload.make,
        model=payload.model,
        year_of_manufacture=payload.year_of_manufacture,
        vin=payload.vin.upper() if payload.vin else None,
        engine_code=payload.engine_code,
        fuel_type=payload.fuel_type,
        current_mileage=payload.current_mileage or 0,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/{vehicle_id}/history", response_model=List[dict])
def get_vehicle_service_history(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    """Vraća kompletnu servisnu istoriju vozila sa ugrađenim delovima."""
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id, Vehicle.shop_id == shop_id)
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vozilo nije pronađeno.")

    orders = (
        db.query(WorkOrder)
        .filter(
            WorkOrder.vehicle_id == vehicle_id,
            WorkOrder.shop_id == shop_id,
            WorkOrder.status.in_([WorkOrderStatus.COMPLETED, WorkOrderStatus.DELIVERED]),
        )
        .order_by(desc(WorkOrder.received_at))
        .all()
    )

    history = []
    for o in orders:
        items = db.query(WorkOrderItem).filter(WorkOrderItem.work_order_id == o.id).all()
        history.append({
            "order_number": o.order_number,
            "date": o.completed_at.strftime("%d.%m.%Y") if o.completed_at else o.received_at.strftime("%d.%m.%Y"),
            "mileage": o.mileage_at_reception,
            "complaint": o.complaint_description,
            "total_amount": float(o.total_amount or 0),
            "parts": [
                {
                    "title": item.title,
                    "quantity": float(item.quantity),
                    "price": float(item.unit_price),
                    "is_part": item.is_part,
                }
                for item in items
            ],
        })

    return history

@router.get("/export/csv")
def export_vehicles_csv(
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
):
    """Izvoz vozila u CSV format."""
    import csv
    import io
    from fastapi.responses import StreamingResponse

    vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.shop_id == shop_id)
        .order_by(Vehicle.license_plate)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "Registracija", "Marka", "Model", "VIN", "Godina",
        "Gorivo", "Kilometraža", "Datum registracije"
    ])

    for v in vehicles:
        writer.writerow([
            v.license_plate or "",
            v.make or "",
            v.model or "",
            v.vin or "",
            v.year_of_manufacture or "",
            v.fuel_type or "",
            v.current_mileage or 0,
            v.last_registered_at.strftime("%d.%m.%Y") if v.last_registered_at else "",
        ])

    output.seek(0)
    content = "\ufeff" + output.getvalue()

    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="vozila.csv"'},
    )