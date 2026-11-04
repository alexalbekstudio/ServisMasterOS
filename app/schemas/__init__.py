
from app.schemas.shop import ShopCreate, ShopUpdate, ShopResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse, Token, TokenPayload
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.schemas.part import PartCreate, PartUpdate, PartResponse
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderUpdate,
    WorkOrderResponse,
    PublicWorkOrderResponse,
    StatusHistoryItem,
    WorkOrderItemCreate,
    WorkOrderItemResponse,
    WorkOrderPhotoCreate,
    WorkOrderPhotoResponse,
)
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    NotificationLogResponse,
)
from app.schemas.fiscal import FiscalReceiptResponse
from app.schemas.auth import ShopRegisterRequest

__all__ = [
    "ShopCreate", "ShopUpdate", "ShopResponse",
    "UserCreate", "UserUpdate", "UserResponse", "Token", "TokenPayload",
    "CustomerCreate", "CustomerUpdate", "CustomerResponse",
    "VehicleCreate", "VehicleUpdate", "VehicleResponse",
    "PartCreate", "PartUpdate", "PartResponse",
    "WorkOrderCreate", "WorkOrderUpdate", "WorkOrderResponse",
    "PublicWorkOrderResponse", "StatusHistoryItem",
    "WorkOrderItemCreate", "WorkOrderItemResponse",
    "WorkOrderPhotoCreate", "WorkOrderPhotoResponse",
    "ReminderCreate", "ReminderUpdate", "ReminderResponse",
    "NotificationLogResponse", "FiscalReceiptResponse",
    "ShopRegisterRequest",
]