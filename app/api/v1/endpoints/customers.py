from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_shop_id
from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter()


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    customer = Customer(
        shop_id=shop_id,
        full_name=payload.full_name,
        phone=payload.phone,
        email=payload.email,
        is_company=payload.is_company,
        company_name=payload.company_name,
        pib=payload.pib,
        notes=payload.notes,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    query = db.query(Customer).filter(Customer.shop_id == shop_id)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Customer.full_name.ilike(s))
            | (Customer.phone.ilike(s))
            | (Customer.company_name.ilike(s))
        )
    return query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.shop_id == shop_id)
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Klijent nije pronađen.")
    return customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> Any:
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.shop_id == shop_id)
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Klijent nije pronađen.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    shop_id: UUID = Depends(get_current_shop_id),
) -> None:
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.shop_id == shop_id)
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Klijent nije pronađen.")
    db.delete(customer)
    db.commit()