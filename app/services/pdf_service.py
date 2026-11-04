import io
import os
import base64
from pathlib import Path
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.models.shop import Shop
from app.models.work_order import WorkOrder
from app.models.vehicle import Vehicle
from app.models.customer import Customer
from app.services.ips_qr_service import IpsQrService


def resolve_logo_path(custom_path: str = None) -> str:
    """Pronalazi apsolutnu putanju do logotipa u projektu."""
    if custom_path and os.path.isabs(custom_path) and os.path.exists(custom_path):
        return custom_path

    current_dir = Path(__file__).resolve().parent
    search_dirs = [
        current_dir,
        current_dir.parent,
        current_dir.parent.parent,
        current_dir.parent.parent.parent,
        Path.cwd(),
    ]

    target_files = [
        custom_path,
        "frontend/img/logo-a.png",
        "img/logo-a.png",
        "static/img/logo-a.png",
    ]

    for s_dir in search_dirs:
        for t_file in target_files:
            if not t_file: continue
            candidate = (s_dir / t_file).resolve()
            if candidate.exists() and candidate.is_file():
                return str(candidate)
    return None


def setup_pdf_fonts():
    """Registruje fontove sa UTF-8 podrškom za srpsku latinicu."""
    font_paths = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"),
        ("C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\arialbd.ttf"),
    ]

    regular_registered = False
    bold_registered = False

    for reg_path, bold_path in font_paths:
        if os.path.exists(reg_path) and not regular_registered:
            try:
                pdfmetrics.registerFont(TTFont("CustomFont", reg_path))
                regular_registered = True
            except Exception:
                pass
        if os.path.exists(bold_path) and not bold_registered:
            try:
                pdfmetrics.registerFont(TTFont("CustomFont-Bold", bold_path))
                bold_registered = True
            except Exception:
                pass
        if regular_registered and bold_registered:
            break

    if regular_registered and not bold_registered:
        pdfmetrics.registerFont(TTFont("CustomFont-Bold", reg_path))

    return "CustomFont" if regular_registered else "Helvetica"


class PdfService:
    FONT_NAME = None
    FONT_BOLD = None

    @classmethod
    def _init_fonts(cls):
        if cls.FONT_NAME is None:
            base_font = setup_pdf_fonts()
            cls.FONT_NAME = base_font
            cls.FONT_BOLD = f"{base_font}-Bold" if base_font != "Helvetica" else "Helvetica-Bold"

    @classmethod
    def generate_work_order_pdf(
        cls, shop: Shop, work_order: WorkOrder, vehicle: Vehicle, customer: Customer
    ) -> bytes:
        cls._init_fonts()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
        )

        elements = []
        styles = getSampleStyleSheet()

        meta_style = ParagraphStyle('MetaStyle', parent=styles['Normal'], fontName=cls.FONT_NAME, fontSize=9, leading=13, textColor=colors.HexColor("#334155"))
        bold_meta = ParagraphStyle('BoldMeta', parent=meta_style, fontName=cls.FONT_BOLD)
        right_meta = ParagraphStyle('RightMeta', parent=meta_style, alignment=TA_RIGHT)
        center_meta = ParagraphStyle('CenterMeta', parent=meta_style, alignment=TA_CENTER)

        # --- 1. ZAGLAVLJE: LOGO + PODACI O SERVISU + NALOG ---
        configured_logo = getattr(shop, 'logo_path', None)
        found_logo_path = resolve_logo_path(configured_logo)

        shop_info = f"""<b>{shop.name}</b><br/>
{shop.address or ''}, {shop.city or ''}<br/>
Tel: {shop.phone or '-'} | PIB: {shop.pib or '-'}<br/>
MB: {shop.maticni_broj or '-'}
"""
        order_meta = f"""<b>RADNI NALOG br: #{work_order.order_number}</b><br/>
Datum prijema: {work_order.received_at.strftime('%d.%m.%Y %H:%M')}<br/>
Status: <b>{getattr(work_order.status, 'value', work_order.status)}</b><br/>
Kilometraža: {work_order.mileage_at_reception:,} km
"""

        if found_logo_path:
            logo_img = Image(found_logo_path, width=20 * mm, height=20 * mm, kind='proportional')
            header_table = Table([[logo_img, Paragraph(shop_info, meta_style), Paragraph(order_meta, right_meta)]], colWidths=[24 * mm, 86 * mm, 70 * mm])
            header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('ALIGN', (0, 0), (0, 0), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
        else:
            header_table = Table([[Paragraph(shop_info, meta_style), Paragraph(order_meta, right_meta)]], colWidths=[105 * mm, 75 * mm])
            header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))

        elements.append(header_table)
        elements.append(Spacer(1, 4 * mm))

        # --- 2. PODACI O KLIJENTU I VOZILU ---
        company_info = f"<br/>{customer.company_name} (PIB: {customer.pib})" if getattr(customer, 'is_company', False) and customer.company_name else ""
        client_data = f"""<b>PODACI O VLASNIKU:</b><br/>{customer.full_name}<br/>Tel: {customer.phone or '-'}{company_info}"""
        vehicle_data = f"""<b>PODACI O VOZILU:</b><br/>Vozilo: <b>{vehicle.make} {vehicle.model}</b><br/>Tablice: <b>{vehicle.license_plate}</b><br/>Šasija (VIN): {vehicle.vin or 'N/A'}<br/>Nivo goriva: {work_order.fuel_level or '-'}"""
        info_table = Table([[Paragraph(client_data, meta_style), Paragraph(vehicle_data, meta_style)]], colWidths=[90 * mm, 90 * mm])
        info_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")), ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")), ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")), ('PADDING', (0, 0), (-1, -1), 6)]))
        elements.append(info_table)
        elements.append(Spacer(1, 4 * mm))

        # --- 3. OPIS PROBLEMA ---
        complaint_text = f"<b>Opis problema / Zahtev klijenta:</b><br/>{work_order.complaint_description or '-'}"
        complaint_table = Table([[Paragraph(complaint_text, meta_style)]], colWidths=[180 * mm])
        complaint_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")), ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")), ('PADDING', (0, 0), (-1, -1), 6)]))
        elements.append(complaint_table)
        elements.append(Spacer(1, 5 * mm))

        # --- 4. TABELA STAVKI ---
        table_rows = [[
            Paragraph("<b>#</b>", bold_meta), Paragraph("<b>Opis rada / Naziv dela</b>", bold_meta),
            Paragraph("<b>Tip</b>", bold_meta), Paragraph("<b>Kol.</b>", bold_meta),
            Paragraph("<b>Cena (RSD)</b>", bold_meta), Paragraph("<b>Iznos (RSD)</b>", bold_meta),
        ]]

        total_labor = Decimal("0.00")
        total_parts = Decimal("0.00")

        for idx, item in enumerate(work_order.items, start=1):
            qty = Decimal(str(item.quantity))
            price = Decimal(str(item.unit_price))
            total = qty * price

            if item.is_part:
                total_parts += total
                type_label = "Deo"
            else:
                total_labor += total
                type_label = "Usluga"

            table_rows.append([
                Paragraph(str(idx), meta_style), Paragraph(item.title, meta_style),
                Paragraph(type_label, meta_style), Paragraph(f"{qty:.2f}", meta_style),
                Paragraph(f"{price:,.2f}", meta_style), Paragraph(f"{total:,.2f}", bold_meta),
            ])

        if len(table_rows) == 1:
            table_rows.append([Paragraph("-", meta_style), Paragraph("Nema unetih stavki", meta_style), Paragraph("-", meta_style), Paragraph("-", meta_style), Paragraph("-", meta_style), Paragraph("0.00", meta_style)])

        items_table = Table(table_rows, colWidths=[8 * mm, 74 * mm, 20 * mm, 22 * mm, 26 * mm, 30 * mm])
        items_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")), ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")), ('PADDING', (0, 0), (-1, -1), 4), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        elements.append(items_table)
        elements.append(Spacer(1, 4 * mm))

        # --- 5. REKAPITULACIJA I IPS QR KOD ---
        grand_total = total_labor + total_parts
        summary_text = f"""<b>Usluge / Rad:</b> {total_labor:,.2f} RSD<br/>
<b>Rezervni delovi:</b> {total_parts:,.2f} RSD<br/>
-------------------------------------------------<br/>
<font size="12"><b>UKUPNO ZA NAPLATU: {grand_total:,.2f} RSD</b></font>
"""
        summary_p = Paragraph(summary_text, meta_style)

        qr_flowable = Paragraph("", meta_style)
        if grand_total > 0 and vehicle:
            try:
                raw_qr_base64 = IpsQrService.get_order_payment_qr(shop, work_order, vehicle)
                if raw_qr_base64:
                    _, b64_data = raw_qr_base64.split(",", 1)
                    qr_img_bytes = base64.b64decode(b64_data)
                    qr_flowable = Image(io.BytesIO(qr_img_bytes), width=34 * mm, height=34 * mm)
            except Exception:
                pass

        summary_table = Table([[qr_flowable, summary_p]], colWidths=[40 * mm, 140 * mm])
        summary_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        elements.append(summary_table)
        elements.append(Spacer(1, 10 * mm))

        # --- 6. POTPISI ---
        signature_table = Table([[
            Paragraph("________________________________<br/>Vozilo primio (Servis)", center_meta),
            Paragraph("________________________________<br/>Vozilo predao (Vlasnik)", center_meta),
        ]], colWidths=[90 * mm, 90 * mm])
        signature_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        elements.append(signature_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()