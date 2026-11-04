import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from urllib.parse import quote
from uuid import UUID

import requests
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.reminder import NotificationLog, Reminder
from app.models.shop import Shop
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder

logger = logging.getLogger(__name__)


class NotificationService:
    # Uzimamo kredencijale iz .env fajla
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_DEV_CHAT_ID", "")

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", ""))
    TEST_EMAIL_RECIPIENT = os.getenv("TEST_EMAIL_RECIPIENT", os.getenv("SMTP_USER", ""))

    @classmethod
    def _build_email_header(cls, shop: Shop) -> str:
        """Generiše HTML zaglavlje email-a sa podacima servisa."""
        shop_name = shop.name if shop else "Auto Centar Master"
        shop_address = shop.address or ""
        shop_city = shop.city or ""
        shop_phone = shop.phone or ""
        shop_email = shop.email or ""

        address_line = f"{shop_address}, {shop_city}" if shop_address and shop_city else shop_city

        contact_parts = []
        if shop_phone: contact_parts.append(f"📞 {shop_phone}")
        if shop_email: contact_parts.append(f"✉️ {shop_email}")
        contact_line = " &nbsp;|&nbsp; ".join(contact_parts)

        return f"""
        <div style="background: #f4f1ec; padding: 20px; border-bottom: 3px solid #d97706; margin-bottom: 20px;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h1 style="color: #1a1a1a; font-size: 22px; margin: 0 0 8px 0; font-weight: 800; letter-spacing: -0.02em;">
                    {shop_name}
                </h1>
                {f'<p style="color: #6b6b6b; font-size: 13px; margin: 4px 0;">{address_line}</p>' if address_line else ''}
                {f'<p style="color: #6b6b6b; font-size: 13px; margin: 4px 0;">{contact_line}</p>' if contact_line else ''}
            </div>
        </div>
        """

    @classmethod
    def _build_email_footer(cls, shop: Shop) -> str:
        """Generiše HTML podnožje email-a."""
        shop_name = shop.name if shop else "Auto Centar Master"
        return f"""
        <div style="max-width: 600px; margin: 20px auto 0; padding-top: 16px; border-top: 1px solid #e5e1d8; text-align: center;">
            <p style="color: #94a3b8; font-size: 11px; margin: 0;">
                Ovaj email je automatski generisan od strane ServisMasterOS.<br/>
                © {shop_name} — Hvala na poverenju.
            </p>
        </div>
        """

    @classmethod
    def send_telegram_message(cls, text: str) -> bool:
        """Šalje poruku na Telegram."""
        if not cls.TELEGRAM_TOKEN or not cls.TELEGRAM_CHAT_ID:
            logger.warning("[Telegram] Nema tokena ili chat ID-a.")
            return False

        url = f"https://api.telegram.org/bot{cls.TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": cls.TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}

        try:
            res = requests.post(url, json=payload, timeout=10)
            data = res.json()
            if not data.get("ok"):
                logger.error(f"[Telegram Błąd API]: {data}")
                return False
            return True
        except Exception as e:
            logger.error(f"[Telegram Błąd połączenia]: {e}")
            return False

    @classmethod
    def send_email_message(
        cls,
        to_email: str,
        subject: str,
        html_content: str,
        pdf_bytes: Optional[bytes] = None,
        pdf_filename: str = "Dokument.pdf",
    ) -> bool:
        """Šalje email preko SMTP."""
        recipient = cls.TEST_EMAIL_RECIPIENT if cls.TEST_EMAIL_RECIPIENT else to_email
        if not cls.SMTP_USER or not cls.SMTP_PASSWORD or not recipient:
            logger.warning("[Email] Nema SMTP kredencijala.")
            return False

        msg = MIMEMultipart()
        msg["From"] = cls.SMTP_FROM
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        if pdf_bytes:
            pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
            pdf_attachment.add_header("Content-Disposition", f'attachment; filename="{pdf_filename}"')
            msg.attach(pdf_attachment)

        try:
            with smtplib.SMTP(cls.SMTP_HOST, cls.SMTP_PORT) as server:
                server.starttls()
                server.login(cls.SMTP_USER, cls.SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"[Email Błąd]: {e}")
            return False

    @classmethod
    def log_notification(
        cls,
        db: Session,
        shop_id: UUID,
        customer_id: Optional[UUID],
        recipient: str,
        message: str,
        channel: str = "SYSTEM",
        is_delivered: bool = True,
    ) -> NotificationLog:
        """Beleži notifikaciju u bazu."""
        log_entry = NotificationLog(
            shop_id=shop_id,
            customer_id=customer_id,
            recipient_phone=recipient,
            channel=channel,
            message=message,
            gateway_message_id=f"msg_{UUID(int=1)}",
            is_delivered=is_delivered,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @classmethod
    def generate_whatsapp_link(cls, phone: str, message: str) -> Optional[str]:
        """Generiše wa.me link za WhatsApp."""
        if not phone: return None
        digits = "".join(c for c in phone if c.isdigit())
        if not digits: return None

        if digits.startswith("0") and len(digits) == 10:
            digits = "381" + digits[1:]
        if not digits.startswith("381") and len(digits) == 9:
            digits = "381" + digits

        encoded_message = quote(message, safe="")
        return f"https://wa.me/{digits}?text={encoded_message}"

    # --- GLAVNE METODE ---
    @classmethod
    def send_order_opened(cls, db: Session, work_order: WorkOrder, base_url: str = "http://localhost:8000") -> bool:
        vehicle = db.query(Vehicle).filter(Vehicle.id == work_order.vehicle_id).first()
        if not vehicle: return False
        customer = db.query(Customer).filter(Customer.id == vehicle.customer_id).first()
        shop = db.query(Shop).filter(Shop.id == work_order.shop_id).first()
        shop_name = shop.name if shop else "Auto Centar Master"
        tracking_link = f"{base_url}/status?token={work_order.tracking_token}"

        tg_text = (
            f"📋 <b>{shop_name} — Prijem vozila na servis</b>\n\n"
            f"Vozilo: <b>{vehicle.make} {vehicle.model} ({vehicle.license_plate})</b>\n"
            f"Klijent: <b>{customer.full_name if customer else 'Stranka'}</b>\n"
            f"Broj naloga: <b>#{work_order.order_number}</b>\n\n"
            f'🔗 <b>Status popravke uživo:</b>\n<a href="{tracking_link}">{tracking_link}</a>'
        )
        tg_success = cls.send_telegram_message(text=tg_text)

        email_to = (customer.email if customer and getattr(customer, "email", None) else None) or cls.TEST_EMAIL_RECIPIENT
        if email_to:
            subject = f"Prijem na servis: {vehicle.make} {vehicle.model} ({vehicle.license_plate})"
            html = f"""
            {cls._build_email_header(shop)}
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 0 20px;">
                <h3 style="color: #0f172a; margin-top: 0;">Poštovani {customer.full_name if customer else ''},</h3>
                <p>Vaše vozilo <b>{vehicle.make} {vehicle.model} ({vehicle.license_plate})</b> uspešno je primljeno na servis (Radni nalog <b>#{work_order.order_number}</b>).</p>
                <p>Status popravke možete pratiti uživo u svakom trenutku:</p>
                <p style="margin: 24px 0; text-align: center;">
                    <a href="{tracking_link}" style="background-color: #d97706; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Prati status vozila</a>
                </p>
            </div>
            {cls._build_email_footer(shop)}
            """
            cls.send_email_message(to_email=email_to, subject=subject, html_content=html)

        cls.log_notification(db, work_order.shop_id, customer.id if customer else None,
                             customer.phone if customer and customer.phone else "TELEGRAM/EMAIL",
                             f"Prijem vozila #{work_order.order_number} ({vehicle.license_plate})",
                             "TELEGRAM/EMAIL", tg_success)
        return True

    @classmethod
    def send_order_completed(cls, db: Session, work_order: WorkOrder, pdf_bytes: Optional[bytes] = None, base_url: str = "http://localhost:8000") -> bool:
        vehicle = db.query(Vehicle).filter(Vehicle.id == work_order.vehicle_id).first()
        if not vehicle: return False
        customer = db.query(Customer).filter(Customer.id == vehicle.customer_id).first()
        shop = db.query(Shop).filter(Shop.id == work_order.shop_id).first()
        shop_name = shop.name if shop else "Auto Centar Master"
        amount = float(work_order.total_amount or 0.0)
        tracking_link = f"{base_url}/status?token={work_order.tracking_token}"

        tg_text = (
            f"🚗 <b>{shop_name} — Vozilo je spremno!</b>\n\n"
            f"Vozilo: <b>{vehicle.make} {vehicle.model} ({vehicle.license_plate})</b>\n"
            f"Klijent: <b>{customer.full_name if customer else 'Stranka'}</b>\n"
            f"Ukupan račun: <b>{amount:,.2f} RSD</b>\n\n"
            f'🔗 <b>Račun i status uživo:</b>\n<a href="{tracking_link}">{tracking_link}</a>'
        )
        tg_success = cls.send_telegram_message(text=tg_text)

        email_to = (customer.email if customer and getattr(customer, "email", None) else None) or cls.TEST_EMAIL_RECIPIENT
        email_success = False
        if email_to:
            subject = f"Servis završen: {vehicle.make} {vehicle.model} ({vehicle.license_plate})"
            html = f"""
            {cls._build_email_header(shop)}
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 0 20px;">
                <h2 style="color: #0f172a; margin-top: 0;">Poštovani {customer.full_name if customer else ''},</h2>
                <p>Radovi na vašem vozilu <b>{vehicle.make} {vehicle.model} ({vehicle.license_plate})</b> su uspešno završeni.</p>
                <div style="background: #dcfce7; border-left: 4px solid #16a34a; padding: 16px; margin: 20px 0; border-radius: 4px;">
                    <p style="margin: 0; font-size: 14px; color: #166534;">Ukupan iznos za naplatu:</p>
                    <p style="margin: 4px 0 0 0; font-size: 24px; font-weight: 800; color: #16a34a;">{amount:,.2f} RSD</p>
                </div>
                <p style="text-align: center; margin: 24px 0;">
                    <a href="{tracking_link}" style="background-color: #d97706; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Pogledaj nalog i račun</a>
                </p>
                <p style="color: #64748b; font-size: 13px;">U prilogu se nalazi generisani PDF račun.</p>
            </div>
            {cls._build_email_footer(shop)}
            """
            email_success = cls.send_email_message(to_email=email_to, subject=subject, html_content=html, pdf_bytes=pdf_bytes, pdf_filename=f"Racun_{vehicle.license_plate}.pdf")

        cls.log_notification(db, work_order.shop_id, customer.id if customer else None,
                             customer.phone if customer and customer.phone else "TELEGRAM/EMAIL",
                             f"Završeno #{work_order.order_number}: {amount:,.2f} RSD",
                             "TELEGRAM/EMAIL", tg_success or email_success)
        return tg_success or email_success

    @classmethod
    def send_status_change(cls, db: Session, work_order: WorkOrder, old_status: str, new_status: str, base_url: str = "http://localhost:8000") -> bool:
        vehicle = db.query(Vehicle).filter(Vehicle.id == work_order.vehicle_id).first()
        if not vehicle: return False
        customer = db.query(Customer).filter(Customer.id == vehicle.customer_id).first()
        shop = db.query(Shop).filter(Shop.id == work_order.shop_id).first()
        tracking_link = f"{base_url}/status?token={work_order.tracking_token}"

        STATUS_MAP = {
            "RECEIVED": ("📥 Primljeno", "Vozilo je primljeno u servis."),
            "DIAGNOSING": ("🔍 Dijagnostika", "Majstor trenutno pregleda vozilo."),
            "WAITING_FOR_PARTS": ("⏳ Čeka delove", "Naručeni su delovi. Čekamo isporuku."),
            "IN_PROGRESS": ("🔧 U radu", "Radovi na vozilu su u toku."),
            "COMPLETED": ("✅ Završeno", "Vozilo je spremno za preuzimanje!"),
            "DELIVERED": ("🎉 Preuzeto", "Vozilo je preuzeto. Hvala na poverenju!"),
        }
        status_label, status_desc = STATUS_MAP.get(new_status, (new_status, "Status je ažuriran."))

        tg_text = (
            f"<b>{shop.name if shop else 'Auto Centar'} — Ažuriranje statusa</b>\n\n"
            f"Vozilo: <b>{vehicle.make} {vehicle.model} ({vehicle.license_plate})</b>\n"
            f"<b>{status_label}</b>\n{status_desc}\n\n"
            f'🔗 <a href="{tracking_link}">Prati status uživo</a>'
        )
        tg_success = cls.send_telegram_message(text=tg_text)

        # (Email deo možeš dodati po istom kalupu ako želiš)
        return tg_success

    @classmethod
    def send_approval_request(cls, db: Session, work_order: WorkOrder, item, base_url: str = "http://localhost:8000") -> bool:
        vehicle = db.query(Vehicle).filter(Vehicle.id == work_order.vehicle_id).first()
        if not vehicle: return False
        customer = db.query(Customer).filter(Customer.id == vehicle.customer_id).first()
        shop = db.query(Shop).filter(Shop.id == work_order.shop_id).first()
        tracking_link = f"{base_url}/status?token={work_order.tracking_token}"
        total = float(item.quantity) * float(item.unit_price)

        tg_text = (
            f"⚠️ <b>{shop.name if shop else 'Auto Centar'} — Potrebno odobrenje</b>\n\n"
            f"Vozilo: <b>{vehicle.make} {vehicle.model} ({vehicle.license_plate})</b>\n"
            f"Majstor je uočio dodatni rad:\n<b>{item.title}</b> — {total:,.2f} RSD\n\n"
            f'🔗 <a href="{tracking_link}">Odobri ili odbij rad</a>'
        )
        return cls.send_telegram_message(text=tg_text)

    @classmethod
    def trigger_reminder(cls, db: Session, reminder: Reminder) -> bool:
        """Šalje podsetnik (registracija, mali servis)."""
        # Ovde ide logika za podsetnike (po potrebi)
        return True