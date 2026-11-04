from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    analytics,
    auth,
    customers,
    fiscal,
    help,
    ocr,
    parts,
    reminders,
    vehicles,
    vin,
    work_orders,
)

api_router = APIRouter()
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Panel"])
api_router.include_router(auth.router, prefix="/auth", tags=["Autentifikacija"])
api_router.include_router(customers.router, prefix="/customers", tags=["Klijenti"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vozila"])
api_router.include_router(work_orders.router, prefix="/work-orders", tags=["Radni Nalozi"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["Podsetnici"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["OCR Skeniranje"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analitika"])
api_router.include_router(parts.router, prefix="/parts", tags=["Magacin"])
api_router.include_router(vin.router, prefix="/vin", tags=["VIN Dekoder"])
api_router.include_router(fiscal.router, prefix="/fiscal", tags=["Fiskalizacija"])
api_router.include_router(help.router, prefix="/help", tags=["Help"])