from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_super_admin
from app.core.security import get_password_hash
from app.database import get_db
from app.models.shop import Shop
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.user import User
from app.models.work_order import WorkOrder

router = APIRouter()


class UpdateSubscriptionRequest(BaseModel):
    plan: SubscriptionPlan | None = None
    status: SubscriptionStatus | None = None
    max_users: int | None = None
    max_work_orders_per_month: int | None = None
    notes: str | None = None


@router.get("/shops")
def list_shops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
) -> List[Dict[str, Any]]:
    """Vraća listu svih registrovanih servisa (pretplatnika)."""
    shops = db.query(Shop).order_by(Shop.created_at.desc()).all()

    result = []
    for shop in shops:
        sub = db.query(Subscription).filter(Subscription.shop_id == shop.id).first()
        owner = db.query(User).filter(User.shop_id == shop.id, User.role == "OWNER").first()
        user_count = db.query(func.count(User.id)).filter(User.shop_id == shop.id).scalar() or 0
        order_count = db.query(func.count(WorkOrder.id)).filter(WorkOrder.shop_id == shop.id).scalar() or 0

        result.append({
            "shop_id": str(shop.id),
            "shop_name": shop.name,
            "shop_city": shop.city,
            "shop_phone": shop.phone,
            "shop_email": shop.email,
            "created_at": shop.created_at.isoformat() if shop.created_at else None,
            "is_active": shop.is_active,
            "owner_name": owner.full_name if owner else None,
            "owner_email": owner.email if owner else None,
            "users_count": user_count,
            "orders_count": order_count,
            "subscription": {
                "plan": sub.plan.value if sub and sub.plan else "NONE",
                "status": sub.status.value if sub and sub.status else "NONE",
                "trial_ends_at": sub.trial_ends_at.isoformat() if sub and sub.trial_ends_at else None,
                "current_period_end": sub.current_period_end.isoformat() if sub and sub.current_period_end else None,
                "max_users": sub.max_users if sub else 1,
                "max_work_orders_per_month": sub.max_work_orders_per_month if sub else 50,
            } if sub else None,
        })

    return result


@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
) -> Dict[str, Any]:
    """Vraća opštu statistiku sistema za super-admina."""
    total_shops = db.query(func.count(Shop.id)).scalar() or 0
    active_shops = db.query(func.count(Shop.id)).filter(Shop.is_active == True).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_orders = db.query(func.count(WorkOrder.id)).scalar() or 0

    plan_counts = db.query(
        Subscription.plan,
        func.count(Subscription.id).label("count"),
    ).group_by(Subscription.plan).all()

    status_counts = db.query(
        Subscription.status,
        func.count(Subscription.id).label("count"),
    ).group_by(Subscription.status).all()

    return {
        "total_shops": total_shops,
        "active_shops": active_shops,
        "total_users": total_users,
        "total_orders": total_orders,
        "plans": {p.value: c for p, c in plan_counts},
        "statuses": {s.value: c for s, c in status_counts},
    }


@router.patch("/shops/{shop_id}/subscription")
def update_shop_subscription(
    shop_id: UUID,
    payload: UpdateSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
) -> Dict[str, Any]:
    """Ažurira pretplatu servisa (plan, status, limite)."""
    sub = db.query(Subscription).filter(Subscription.shop_id == shop_id).first()

    if not sub:
        sub = Subscription(shop_id=shop_id)
        db.add(sub)

    if payload.plan:
        sub.plan = payload.plan
    if payload.status:
        sub.status = payload.status
    if payload.max_users is not None:
        sub.max_users = payload.max_users
    if payload.max_work_orders_per_month is not None:
        sub.max_work_orders_per_month = payload.max_work_orders_per_month
    if payload.notes is not None:
        sub.notes = payload.notes

    sub.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(sub)

    return {
        "shop_id": str(sub.shop_id),
        "plan": sub.plan.value if sub.plan else None,
        "status": sub.status.value if sub.status else None,
        "max_users": sub.max_users,
        "max_work_orders_per_month": sub.max_work_orders_per_month,
    }


@router.patch("/shops/{shop_id}/toggle-active")
def toggle_shop_active(
    shop_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
) -> Dict[str, Any]:
    """Aktivira/deaktivira servis."""
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Servis nije pronađen.")

    shop.is_active = not shop.is_active
    db.commit()
    db.refresh(shop)

    return {
        "shop_id": str(shop.id),
        "is_active": shop.is_active,
    }