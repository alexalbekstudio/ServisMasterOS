from datetime import date
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_shop_id
from app.database import get_db
from app.models.enums import ReminderStatus
from app.models.reminder import NotificationLog, Reminder
from app.models.vehicle import Vehicle
from app.schemas.reminder import (
    NotificationLogResponse,
    ReminderCreate,
    ReminderResponse,
    ReminderUpdate,
)
from app.services.notification_service import NotificationService

router = APIRouter()


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    vehicle = db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id, Vehicle.shop_id == shop_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vozilo nije pronađeno u vašem servisu.")

    reminder = Reminder(
        shop_id=shop_id,
        vehicle_id=payload.vehicle_id,
        type=payload.type,
        due_date=payload.due_date,
        due_mileage=payload.due_mileage,
        scheduled_for=payload.scheduled_for,
        message_text=payload.message_text,
        status=ReminderStatus.PENDING,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("/", response_model=List[ReminderResponse])
def list_reminders(
    status_filter: Optional[ReminderStatus] = Query(None, alias="status"),
    vehicle_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    query = db.query(Reminder).filter(Reminder.shop_id == shop_id)
    if status_filter:
        query = query.filter(Reminder.status == status_filter)
    if vehicle_id:
        query = query.filter(Reminder.vehicle_id == vehicle_id)
    return query.order_by(Reminder.scheduled_for.asc()).offset(skip).limit(limit).all()


@router.patch("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: UUID,
    payload: ReminderUpdate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.shop_id == shop_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Podsetnik nije pronađen.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(reminder, field, value)

    db.commit()
    db.refresh(reminder)
    return reminder


@router.post("/process-due", response_model=dict)
def process_due_reminders(
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    today = date.today()
    due_reminders = (
        db.query(Reminder)
        .filter(
            Reminder.shop_id == shop_id,
            Reminder.status == ReminderStatus.PENDING,
            Reminder.scheduled_for <= today,
        )
        .all()
    )

    sent_count = 0
    failed_count = 0
    for rem in due_reminders:
        success = NotificationService.trigger_reminder(db, rem)
        if success:
            rem.status = ReminderStatus.SENT
            sent_count += 1
        else:
            rem.status = ReminderStatus.FAILED
            failed_count += 1

    db.commit()
    return {
        "status": "completed",
        "processed_date": str(today),
        "sent_count": sent_count,
        "failed_count": failed_count,
    }


@router.get("/logs", response_model=List[NotificationLogResponse])
def list_notification_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    return (
        db.query(NotificationLog)
        .filter(NotificationLog.shop_id == shop_id)
        .order_by(NotificationLog.sent_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )