"""Test da li config čita .env."""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

print("=== Test .env učitavanja ===\n")

# 1. Provera da li .env postoji
env_path = BASE_DIR / ".env"
print(f"1. .env fajl postoji: {'✅' if env_path.exists() else '❌'}")
print(f"   Putanja: {env_path}")

# 2. Provera da li python-dotenv može da ga učita
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=str(env_path), override=True)
    print(f"2. python-dotenv učitavanje: ✅")
except Exception as e:
    print(f"2. python-dotenv učitavanje: ❌ {e}")

# 3. Provera šta je u os.environ
print(f"\n3. Vrednosti iz os.environ:")
print(f"   SMTP_USER: {os.getenv('SMTP_USER', '❌ NEMA')}")
print(f"   SMTP_PASSWORD: {'✅ POSTOJI' if os.getenv('SMTP_PASSWORD') else '❌ NEMA'}")
print(f"   TELEGRAM_BOT_TOKEN: {'✅ POSTOJI' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ NEMA'}")

# 4. Provera kroz settings
print(f"\n4. Vrednosti iz settings (Pydantic):")
from app.config import settings
print(f"   SMTP_USER: {settings.SMTP_USER or '❌ NEMA'}")
print(f"   SMTP_PASSWORD: {'✅ POSTOJI' if settings.SMTP_PASSWORD else '❌ NEMA'}")
print(f"   TELEGRAM_BOT_TOKEN: {'✅ POSTOJI' if settings.TELEGRAM_BOT_TOKEN else '❌ NEMA'}")

# 5. Provera NotificationService
print(f"\n5. Vrednosti iz NotificationService:")
from app.services.notification_service import NotificationService
print(f"   SMTP_USER: {NotificationService.SMTP_USER or '❌ NEMA'}")
print(f"   SMTP_PASSWORD: {'✅ POSTOJI' if NotificationService.SMTP_PASSWORD else '❌ NEMA'}")
print(f"   TELEGRAM_TOKEN: {'✅ POSTOJI' if NotificationService.TELEGRAM_TOKEN else '❌ NEMA'}")
print(f"   TELEGRAM_CHAT_ID: {NotificationService.TELEGRAM_CHAT_ID or '❌ NEMA'}")