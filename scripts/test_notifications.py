"""Test Telegram i Email notifikacija."""
import os
import sys
from pathlib import Path

# ✅ PRVO: Učitaj .env pre bilo čega drugog
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(dotenv_path=str(BASE_DIR / ".env"), override=True)

# ✅ SADA učitaj NotificationService (videće .env vrednosti)
from app.services.notification_service import NotificationService


def test_telegram():
    print("\n=== Test Telegram ===")
    print(f"Token: {'✅ POSTOJI' if NotificationService.TELEGRAM_TOKEN else '❌ NE POSTOJI'}")
    print(f"Chat ID: {NotificationService.TELEGRAM_CHAT_ID or '❌ NE POSTOJI'}")

    if not NotificationService.TELEGRAM_TOKEN or not NotificationService.TELEGRAM_CHAT_ID:
        print("❌ Telegram kredencijali nisu podešeni.")
        return False

    success = NotificationService.send_telegram_message(
        text="🧪 Test iz ServisMasterOS — Telegram radi!\n\nOvo je test poruka."
    )
    print(f"Rezultat: {'✅ USPEH' if success else '❌ NEUSPEH'}")
    return success


def test_email():
    print("\n=== Test Email ===")
    print(f"SMTP User: {NotificationService.SMTP_USER or '❌ NE POSTOJI'}")
    print(f"SMTP Password: {'✅ POSTOJI' if NotificationService.SMTP_PASSWORD else '❌ NE POSTOJI'}")
    print(f"Recipient: {NotificationService.TEST_EMAIL_RECIPIENT or '❌ NE POSTOJI'}")

    if not NotificationService.SMTP_USER or not NotificationService.SMTP_PASSWORD:
        print("❌ Email kredencijali nisu podešeni.")
        return False

    success = NotificationService.send_email_message(
        to_email=NotificationService.TEST_EMAIL_RECIPIENT or "test@example.com",
        subject="Test ServisMasterOS — Email radi!",
        html_content="""
        <div style="font-family: Arial; max-width: 600px; padding: 20px;">
            <h1 style="color: #d97706;">✅ Test uspešan!</h1>
            <p>Ako vidiš ovaj email, SMTP je ispravno podešen.</p>
            <p style="color: #64748b; font-size: 12px;">ServisMasterOS</p>
        </div>
        """
    )
    print(f"Rezultat: {'✅ USPEH' if success else '❌ NEUSPEH'}")
    return success


if __name__ == "__main__":
    print("=== Test Notifikacija ===")
    tg = test_telegram()
    em = test_email()

    print("\n=== Zaključak ===")
    print(f"Telegram: {'✅' if tg else '❌'}")
    print(f"Email:    {'✅' if em else '❌'}")