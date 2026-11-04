from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.vin_decoder_service import VinDecoderService

router = APIRouter()


class VinDecodeRequest(BaseModel):
    vin: str


@router.post("/decode", response_model=Dict[str, Any])
def decode_vin(
    payload: VinDecodeRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Dekodira VIN i vraća podatke o vozilu."""
    vin = payload.vin.strip().upper()

    if not vin:
        raise HTTPException(status_code=400, detail="VIN je obavezan.")

    return VinDecoderService.decode(vin)