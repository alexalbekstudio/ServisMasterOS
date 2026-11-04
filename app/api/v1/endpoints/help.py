from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import PlainTextResponse

from app.services.pdf_service import PdfService

router = APIRouter()

# Putanja do HELP.md
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
HELP_MD_PATH = BASE_DIR / "HELP.md"


@router.get("/markdown", response_class=PlainTextResponse)
def get_help_markdown() -> Any:
    """Vraća HELP.md fajl kao plain text."""
    if not HELP_MD_PATH.exists():
        raise HTTPException(status_code=404, detail="HELP.md nije pronađen.")
    return HELP_MD_PATH.read_text(encoding="utf-8")


@router.get("/pdf")
def get_help_pdf() -> Any:
    """Generiše PDF sa uputstvom iz HELP.md."""
    if not HELP_MD_PATH.exists():
        raise HTTPException(status_code=404, detail="HELP.md nije pronađen.")

    markdown = HELP_MD_PATH.read_text(encoding="utf-8")
    pdf_bytes = PdfService.generate_help_pdf(markdown)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="ServisMasterOS_Uputstvo.pdf"'},
    )