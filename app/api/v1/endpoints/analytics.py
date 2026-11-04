from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_shop_id
from app.database import get_db
from app.models.enums import UserRole, WorkOrderStatus
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder

router = APIRouter()


@router.get("/summary", response_model=Dict[str, Any])
def get_shop_analytics_summary(
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    """Vraća ključne KPI parametre servisa."""
    now = datetime.now(timezone.utc)
    start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    completion_date_col = func.coalesce(
        WorkOrder.completed_at, WorkOrder.updated_at, WorkOrder.created_at
    )

    monthly_orders = (
        db.query(WorkOrder)
        .filter(
            WorkOrder.shop_id == shop_id,
            WorkOrder.status.in_([WorkOrderStatus.COMPLETED, WorkOrderStatus.DELIVERED]),
            completion_date_col >= start_of_month,
        )
        .all()
    )

    monthly_revenue = sum([float(o.total_amount or 0) for o in monthly_orders])
    monthly_completed_count = len(monthly_orders)
    avg_ticket = (monthly_revenue / monthly_completed_count) if monthly_completed_count > 0 else 0.0

    active_in_progress = (
        db.query(func.count(WorkOrder.id))
        .filter(
            WorkOrder.shop_id == shop_id,
            WorkOrder.status.in_([WorkOrderStatus.RECEIVED, WorkOrderStatus.IN_PROGRESS]),
        )
        .scalar()
        or 0
    )

    revenue_split = (
        db.query(
            func.coalesce(func.sum(WorkOrder.total_labor), 0).label("total_labor"),
            func.coalesce(func.sum(WorkOrder.total_parts), 0).label("total_parts"),
            func.coalesce(func.sum(WorkOrder.total_amount), 0).label("all_time_revenue"),
        )
        .filter(
            WorkOrder.shop_id == shop_id,
            WorkOrder.status.in_([WorkOrderStatus.COMPLETED, WorkOrderStatus.DELIVERED]),
        )
        .first()
    )

    top_makes_query = (
        db.query(Vehicle.make, func.count(WorkOrder.id).label("visit_count"))
        .join(WorkOrder, WorkOrder.vehicle_id == Vehicle.id)
        .filter(WorkOrder.shop_id == shop_id)
        .group_by(Vehicle.make)
        .order_by(func.count(WorkOrder.id).desc())
        .limit(3)
        .all()
    )

    top_makes = [{"make": row[0], "count": row[1]} for row in top_makes_query]

    return {
        "monthly_revenue": float(monthly_revenue),
        "monthly_completed_count": monthly_completed_count,
        "average_ticket": float(avg_ticket),
        "active_orders_count": int(active_in_progress),
        "all_time_revenue": float(revenue_split.all_time_revenue if revenue_split else 0),
        "total_labor": float(revenue_split.total_labor if revenue_split else 0),
        "total_parts": float(revenue_split.total_parts if revenue_split else 0),
        "top_makes": top_makes,
    }


@router.get("/mechanics", response_model=Dict[str, Any])
def get_mechanics_performance(
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
    period_days: int = 30,
) -> Any:
    """Vraća učinak majstora u poslednjih N dana."""
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=period_days)

    mechanics = (
        db.query(User)
        .filter(
            User.shop_id == shop_id,
            User.role == UserRole.MECHANIC,
            User.is_active == True,
        )
        .all()
    )

    results = []
    for mech in mechanics:
        completed_orders = (
            db.query(WorkOrder)
            .filter(
                WorkOrder.shop_id == shop_id,
                WorkOrder.assigned_mechanic_id == mech.id,
                WorkOrder.status.in_([WorkOrderStatus.COMPLETED, WorkOrderStatus.DELIVERED]),
                func.coalesce(
                    WorkOrder.completed_at, WorkOrder.updated_at, WorkOrder.created_at,
                ) >= start_date,
            )
            .all()
        )

        active_orders = (
            db.query(func.count(WorkOrder.id))
            .filter(
                WorkOrder.shop_id == shop_id,
                WorkOrder.assigned_mechanic_id == mech.id,
                WorkOrder.status.in_([WorkOrderStatus.RECEIVED, WorkOrderStatus.IN_PROGRESS]),
            )
            .scalar()
            or 0
        )

        total_revenue = sum(float(o.total_amount or 0) for o in completed_orders)
        total_labor = sum(float(o.total_labor or 0) for o in completed_orders)
        total_parts = sum(float(o.total_parts or 0) for o in completed_orders)
        completed_count = len(completed_orders)
        avg_ticket = (total_revenue / completed_count) if completed_count > 0 else 0.0

        results.append({
            "mechanic_id": str(mech.id),
            "mechanic_name": mech.full_name,
            "role": mech.role.value if mech.role else "MECHANIC",
            "completed_orders": completed_count,
            "active_orders": int(active_orders),
            "total_revenue": float(total_revenue),
            "total_labor": float(total_labor),
            "total_parts": float(total_parts),
            "average_ticket": float(avg_ticket),
        })

    results.sort(key=lambda x: x["total_revenue"], reverse=True)

    return {
        "period_days": period_days,
        "start_date": start_date.isoformat(),
        "mechanics": results,
    }