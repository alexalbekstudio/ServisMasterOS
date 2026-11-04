-- Ekstenzije
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ENUMI
CREATE TYPE user_role AS ENUM ('OWNER', 'MECHANIC', 'RECEPTIONIST');
CREATE TYPE work_order_status AS ENUM ('RECEIVED', 'DIAGNOSING', 'WAITING_FOR_PARTS', 'IN_PROGRESS', 'COMPLETED', 'DELIVERED', 'CANCELLED');
CREATE TYPE photo_category AS ENUM ('INITIAL_DAMAGE', 'DEFECT', 'REPLACED_OLD_PART', 'NEW_PART_INSTALLED', 'FINAL');
CREATE TYPE reminder_type AS ENUM ('SMALL_SERVICE', 'BIG_SERVICE', 'REGISTRATION', 'BRAKE_FLUID', 'CUSTOM');
CREATE TYPE reminder_status AS ENUM ('PENDING', 'SENT', 'FAILED', 'DISMISSED');
CREATE TYPE inventory_change_reason AS ENUM ('MANUAL_IN', 'WORK_ORDER_USED', 'WORK_ORDER_RETURN', 'CLIENT_REJECTED', 'ORDER_CANCELLED', 'CORRECTION');

-- 1. Servisi (radionice)
CREATE TABLE shops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    pib VARCHAR(20),
    maticni_broj VARCHAR(20),
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(120),
    address VARCHAR(255),
    city VARCHAR(100) DEFAULT 'Beograd',
    currency VARCHAR(10) DEFAULT 'RSD',
    sms_sender_name VARCHAR(11) DEFAULT 'SERVIS',
    bank_account VARCHAR(30),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Korisnici
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(50),
    role user_role DEFAULT 'MECHANIC',
    theme_preference VARCHAR(10) DEFAULT 'auto',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(shop_id, email)
);

-- 3. Klijenti
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(120),
    is_company BOOLEAN DEFAULT FALSE,
    company_name VARCHAR(150),
    pib VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Vozila
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    license_plate VARCHAR(20) NOT NULL,
    vin VARCHAR(17),
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year_of_manufacture INT,
    engine_code VARCHAR(50),
    fuel_type VARCHAR(30),
    last_registered_at DATE,
    current_mileage INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(shop_id, license_plate)
);

-- 5. Radni nalozi
CREATE TABLE work_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    assigned_mechanic_id UUID REFERENCES users(id) ON DELETE SET NULL,
    order_number INT NOT NULL,
    tracking_token VARCHAR(64) UNIQUE NOT NULL DEFAULT md5(random()::text || clock_timestamp()::text),
    status work_order_status DEFAULT 'RECEIVED',
    mileage_at_reception INT NOT NULL,
    fuel_level VARCHAR(20),
    complaint_description TEXT NOT NULL,
    internal_notes TEXT,
    total_labor NUMERIC(12,2) DEFAULT 0.00,
    total_parts NUMERIC(12,2) DEFAULT 0.00,
    total_amount NUMERIC(12,2) DEFAULT 0.00,
    received_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Stavke naloga
CREATE TABLE work_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    is_part BOOLEAN DEFAULT FALSE,
    title VARCHAR(255) NOT NULL,
    quantity NUMERIC(8,2) DEFAULT 1.00,
    unit_price NUMERIC(12,2) NOT NULL,
    total_price NUMERIC(12,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    requires_approval BOOLEAN DEFAULT FALSE NOT NULL,
    is_approved BOOLEAN,
    approved_at TIMESTAMPTZ,
    inventory_item_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Fotografije
CREATE TABLE work_order_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    category photo_category NOT NULL,
    photo_url TEXT NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Istorija statusa
CREATE TABLE work_order_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    status work_order_status NOT NULL,
    changed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    note VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Podsetnici
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    type reminder_type NOT NULL,
    due_date DATE,
    due_mileage INT,
    status reminder_status DEFAULT 'PENDING',
    scheduled_for DATE NOT NULL,
    message_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. Dnevnik notifikacija
CREATE TABLE notification_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    recipient_phone VARCHAR(50) NOT NULL,
    channel VARCHAR(20) DEFAULT 'SMS',
    message TEXT NOT NULL,
    gateway_message_id VARCHAR(100),
    is_delivered BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. Magacin (delovi)
CREATE TABLE parts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    sku VARCHAR(50),
    name VARCHAR(150) NOT NULL,
    purchase_price NUMERIC(10,2) DEFAULT 0.00 NOT NULL,
    selling_price NUMERIC(10,2) DEFAULT 0.00 NOT NULL,
    quantity INT DEFAULT 0 NOT NULL,
    min_quantity INT DEFAULT 2 NOT NULL
);

-- 12. Inventory log
CREATE TABLE inventory_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    part_id UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    work_order_id UUID REFERENCES work_orders(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    change_quantity NUMERIC(10,2) NOT NULL,
    previous_quantity NUMERIC(10,2) NOT NULL,
    new_quantity NUMERIC(10,2) NOT NULL,
    reason inventory_change_reason NOT NULL,
    note VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. Fiskalni računi
CREATE TABLE fiscal_receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    receipt_number VARCHAR(50) NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL,
    tax_base NUMERIC(12,2) NOT NULL,
    vat_amount NUMERIC(12,2) NOT NULL,
    vat_rate NUMERIC(5,2) DEFAULT 20.00,
    pfr_response JSONB,
    pfr_status VARCHAR(20) DEFAULT 'PENDING',
    verification_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indeksi
CREATE INDEX idx_customers_shop_phone ON customers(shop_id, phone);
CREATE INDEX idx_vehicles_shop_plate ON vehicles(shop_id, license_plate);
CREATE INDEX idx_work_orders_tracking_token ON work_orders(tracking_token);
CREATE INDEX idx_work_orders_shop_status ON work_orders(shop_id, status);
CREATE INDEX idx_reminders_scheduled_status ON reminders(scheduled_for, status);
CREATE INDEX idx_work_order_status_history_order ON work_order_status_history(work_order_id);
CREATE INDEX idx_parts_shop_sku ON parts(shop_id, sku);