import sys
import os
from datetime import date, timedelta, datetime, timezone
from decimal import Decimal

# Dodajemo root projekta u sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.enums import (
    UserRole, WorkOrderStatus, PhotoCategory, ReminderType, ReminderStatus,
)
from app.models.shop import Shop
from app.models.user import User
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder, WorkOrderItem, WorkOrderPhoto
from app.models.reminder import Reminder, NotificationLog


def seed():
    print("Inicijalizujem bazu i unosim početne podatke...")

    # 1. Ekstenzije za UUID
    with engine.connect() as connection:
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))
        connection.commit()

    # 2. Kreiranje tabela
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Provera da li već postoji servis
        existing_shop = db.query(Shop).filter(Shop.name == "Auto Centar Master").first()
        if existing_shop:
            print("Podaci već postoje. Preskačem seed.")
            return

        # 3. Servis (radionica)
        shop = Shop(
            name="Auto Centar Master",
            pib="108923451",
            maticni_broj="20912345",
            phone="013/333-444",
            email="kontakt@autocentarmaster.rs",
            address="Bavaništanski put 12",
            city="Pančevo",
            currency="RSD",
            sms_sender_name="AC_MASTER",
            is_active=True,
        )
        db.add(shop)
        db.flush()

        # 4. Korisnici
        owner = User(
            shop_id=shop.id,
            email="vlasnik@autocentarmaster.rs",
            password_hash=get_password_hash("sifra123"),
            full_name="Marko Petrović",
            phone="064/111-2222",
            role=UserRole.OWNER,
            is_active=True,
        )
        mechanic = User(
            shop_id=shop.id,
            email="majstor@autocentarmaster.rs",
            password_hash=get_password_hash("sifra123"),
            full_name="Dragan Jovanović",
            phone="065/333-4444",
            role=UserRole.MECHANIC,
            is_active=True,
        )
        db.add_all([owner, mechanic])
        db.flush()

        # 5. Klijenti
        customer1 = Customer(
            shop_id=shop.id,
            full_name="Nikola Lukić",
            phone="063/888-9999",
            email="nikola.lukic@gmail.com",
            is_company=False,
            notes="Redovan klijent, uvek traži originalne delove.",
        )
        customer2 = Customer(
            shop_id=shop.id,
            full_name="TransLogistic DOO",
            phone="062/777-6666",
            email="office@translogistic.rs",
            is_company=True,
            company_name="TransLogistic DOO",
            pib="109876543",
        )
        db.add_all([customer1, customer2])
        db.flush()

        # 6. Vozila
        vehicle1 = Vehicle(
            shop_id=shop.id,
            customer_id=customer1.id,
            license_plate="PA-123-AA",
            vin="VF1JZ000055123456",
            make="Renault",
            model="Megane III 1.5 dCi",
            year_of_manufacture=2012,
            engine_code="K9K",
            fuel_type="Dizel",
            last_registered_at=date.today() + timedelta(days=20),
            current_mileage=198500,
        )
        vehicle2 = Vehicle(
            shop_id=shop.id,
            customer_id=customer2.id,
            license_plate="BG-987-ZZ",
            vin="WVWZZZ3CZBE123456",
            make="Volkswagen",
            model="Passat B7 Variant",
            year_of_manufacture=2014,
            engine_code="CFFB",
            fuel_type="Dizel",
            last_registered_at=date.today() + timedelta(days=120),
            current_mileage=245000,
        )
        db.add_all([vehicle1, vehicle2])
        db.flush()

        # 7. Radni nalog
        work_order = WorkOrder(
            shop_id=shop.id,
            vehicle_id=vehicle1.id,
            assigned_mechanic_id=mechanic.id,
            order_number=1,
            mileage_at_reception=198500,
            fuel_level="1/2",
            complaint_description="Lupa u prednjem trapu pri prelasku preko ležećih policajaca. Odraditi i redovan mali servis.",
            internal_notes="Proveriti desnu sponu i silent blokove.",
            status=WorkOrderStatus.IN_PROGRESS,
            total_labor=Decimal("4500.00"),
            total_parts=Decimal("9800.00"),
            total_amount=Decimal("14300.00"),
        )
        db.add(work_order)
        db.flush()

        # 8. Stavke naloga
        items = [
            WorkOrderItem(
                work_order_id=work_order.id,
                is_part=False,
                title="Mali servis (zamena ulja i svih filtera)",
                quantity=Decimal("1.00"),
                unit_price=Decimal("2500.00"),
            ),
            WorkOrderItem(
                work_order_id=work_order.id,
                is_part=False,
                title="Zamena desne spone i centriranje trapa",
                quantity=Decimal("1.00"),
                unit_price=Decimal("2000.00"),
            ),
            WorkOrderItem(
                work_order_id=work_order.id,
                is_part=True,
                title="Motorno ulje Elf Evolution 5W-30 (5L)",
                quantity=Decimal("1.00"),
                unit_price=Decimal("4800.00"),
            ),
            WorkOrderItem(
                work_order_id=work_order.id,
                is_part=True,
                title="Filter ulja Mann",
                quantity=Decimal("1.00"),
                unit_price=Decimal("1200.00"),
            ),
            WorkOrderItem(
                work_order_id=work_order.id,
                is_part=True,
                title="Desna spona Lemförder",
                quantity=Decimal("1.00"),
                unit_price=Decimal("3800.00"),
            ),
        ]
        db.add_all(items)

        # 9. Foto-dokazi (NOVA SLIKA)
        photo = WorkOrderPhoto(
            work_order_id=work_order.id,
            category=PhotoCategory.INITIAL_DAMAGE,
            photo_url="https://images.unsplash.com/photo-1494976388531-d1058494cdd8?auto=format&fit=crop&w=600&q=80",
            description="Zatečena ogrebotina na desnom prednjem blatobranu pri prijemu.",
        )
        db.add(photo)

        # 10. Podsetnik
        reminder = Reminder(
            shop_id=shop.id,
            vehicle_id=vehicle1.id,
            type=ReminderType.REGISTRATION,
            due_date=vehicle1.last_registered_at,
            scheduled_for=date.today(),
            status=ReminderStatus.PENDING,
            message_text=None,
        )
        db.add(reminder)

        # 11. Završen radni nalog (za KPI statistiku)
        completed_order = WorkOrder(
            shop_id=shop.id,
            vehicle_id=vehicle2.id,
            assigned_mechanic_id=mechanic.id,
            order_number=2,
            mileage_at_reception=245000,
            fuel_level="3/4",
            complaint_description="Redovan veliki servis + zamena kočionih pločica.",
            status=WorkOrderStatus.COMPLETED,
            total_labor=Decimal("6500.00"),
            total_parts=Decimal("22000.00"),
            total_amount=Decimal("28500.00"),
            completed_at=datetime.now(timezone.utc),
        )
        db.add(completed_order)
        db.flush()

        # Stavke za završen nalog
        completed_items = [
            WorkOrderItem(
                work_order_id=completed_order.id,
                is_part=False,
                title="Veliki servis (kaiš, pumpa, roleri)",
                quantity=Decimal("1.00"),
                unit_price=Decimal("4500.00"),
            ),
            WorkOrderItem(
                work_order_id=completed_order.id,
                is_part=False,
                title="Zamena prednjih kočionih pločica",
                quantity=Decimal("1.00"),
                unit_price=Decimal("2000.00"),
            ),
            WorkOrderItem(
                work_order_id=completed_order.id,
                is_part=True,
                title="Set zupčastog kaiša Continental",
                quantity=Decimal("1.00"),
                unit_price=Decimal("12000.00"),
            ),
            WorkOrderItem(
                work_order_id=completed_order.id,
                is_part=True,
                title="Prednje kočione pločice ATE",
                quantity=Decimal("1.00"),
                unit_price=Decimal("10000.00"),
            ),
        ]
        db.add_all(completed_items)

        db.commit()
        print("\n✅ Podaci su uspešno ubačeni u bazu!")
        print("-----------------------------------------------------")
        print("Prijava za testiranje:")
        print("Email:    vlasnik@autocentarmaster.rs")
        print("Lozinka:  sifra123")
        print(f"Javni link klijenta (token): {work_order.tracking_token}")
        print("-----------------------------------------------------")

    except Exception as e:
        db.rollback()
        print(f"❌ Greška pri unosu: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()