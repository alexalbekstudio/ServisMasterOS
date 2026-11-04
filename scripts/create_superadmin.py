"""Kreira superadmin nalog za pristup admin panelu."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(dotenv_path=str(BASE_DIR / ".env"), override=True)

from app.database import SessionLocal
from app.core.security import get_password_hash
from app.models.enums import UserRole
from app.models.shop import Shop
from app.models.user import User

# =====================================================
# PODACI ZA SUPERADMIN NALOG
# =====================================================
SUPERADMIN_EMAIL = "alexalbekstudio.design@gmail.com"
SUPERADMIN_PASSWORD = "ServiceMasterOS"   # <-- tvoja lozinka
SUPERADMIN_NAME = "Aleksandar (Superadmin)"
SUPERADMIN_PHONE = "0601234567"


def create_superadmin():
    print("=== Kreiranje superadmin naloga ===\n")

    db = SessionLocal()
    try:
        # 1. Proveri da li korisnik već postoji
        existing_user = db.query(User).filter(User.email == SUPERADMIN_EMAIL).first()
        if existing_user:
            print(f"✅ Korisnik sa email-om {SUPERADMIN_EMAIL} već postoji.")
            print(f"   Ime: {existing_user.full_name}")
            print(f"   Rola: {existing_user.role}")
            print(f"   Aktivan: {existing_user.is_active}")

            response = input("\nDa li želiš da ažuriraš lozinku? (y/n): ")
            if response.lower() == "y":
                existing_user.password_hash = get_password_hash(SUPERADMIN_PASSWORD)
                db.commit()
                print(f"\n✅ Lozinka ažurirana na: {SUPERADMIN_PASSWORD}")
            return

        # 2. Pronađi ili kreiraj shop za superadmin
        shop = db.query(Shop).first()
        if not shop:
            print("Nema shopa u bazi. Kreiram 'ServisMasterOS Admin'...")
            shop = Shop(
                name="ServisMasterOS Admin",
                phone="0601234567",
                email=SUPERADMIN_EMAIL,
                city="Beograd",
            )
            db.add(shop)
            db.flush()
            print(f"✅ Shop kreiran: {shop.name} (ID: {shop.id})")
        else:
            print(f"✅ Koristim postojeći shop: {shop.name}")

        # 3. Kreiraj superadmin korisnika
        superadmin = User(
            shop_id=shop.id,
            email=SUPERADMIN_EMAIL,
            password_hash=get_password_hash(SUPERADMIN_PASSWORD),
            full_name=SUPERADMIN_NAME,
            phone=SUPERADMIN_PHONE,
            role=UserRole.OWNER,
            is_active=True,
        )
        db.add(superadmin)
        db.commit()
        db.refresh(superadmin)

        print(f"\n✅ Superadmin nalog uspešno kreiran!")
        print(f"   Email:    {SUPERADMIN_EMAIL}")
        print(f"   Lozinka:  {SUPERADMIN_PASSWORD}")
        print(f"   Shop ID:  {superadmin.shop_id}")
        print(f"\n⚠️  OBAVEZNO promeni lozinku nakon prve prijave!")

    except Exception as e:
        db.rollback()
        print(f"❌ Greška: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_superadmin()