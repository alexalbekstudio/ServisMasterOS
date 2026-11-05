/**
 * i18n — Internacionalizacija (SR + EN)
 */

const TRANSLATIONS = {
    sr: {
        // Navigacija
        "nav.reception": "Prijem Vozila",
        "nav.orders": "Nalozi u radu",
        "nav.dashboard": "Kontrolna Tabla",
        "nav.inventory": "Magacin",
        "nav.reminders": "SMS Podsetnici",
        "nav.admin": "Admin",

        // Header
        "header.logout": "Odjava",
        "header.help": "Pomoć",
        "header.guide": "Uputstvo",
        "header.language": "Jezik",

        // Login
        "login.title": "Dobrodošli nazad",
        "login.subtitle": "Prijavite se na vaš ServisMasterOS nalog",
        "login.email": "Email adresa",
        "login.password": "Lozinka",
        "login.submit": "Prijavi se",
        "login.no_account": "Nemate nalog?",
        "login.register_link": "Registrujte svoj servis",

        // Register
        "register.title": "Registrujte svoj servis",
        "register.subtitle": "Napravite nalog za vašu radionicu u 30 sekundi",
        "register.shop_section": "Podaci o servisu",
        "register.shop_name": "Naziv servisa",
        "register.shop_phone": "Telefon servisa",
        "register.shop_city": "Grad",
        "register.owner_section": "Podaci o vlasniku",
        "register.owner_name": "Ime i prezime",
        "register.owner_email": "Email adresa (za prijavu)",
        "register.owner_password": "Lozinka (min. 6 znakova)",
        "register.submit": "Registruj servis",
        "register.have_account": "Već imate nalog?",
        "register.login_link": "Prijavite se",

        // Prijem vozila
        "reception.customer_section": "1. Podaci o vlasniku",
        "reception.customer_search": "Pretraga postojećeg klijenta",
        "reception.customer_name": "Ime i prezime",
        "reception.customer_phone": "Telefon (za SMS)",
        "reception.vehicle_section": "2. Vozilo",
        "reception.ocr_title": "Pametno očitavanje saobraćajne dozvole",
        "reception.ocr_camera": "Kamera Uživo",
        "reception.ocr_file": "Izaberi Sliku",
        "reception.ocr_manual": "Ručni unos",
        "reception.plate": "Registarska oznaka",
        "reception.make": "Marka",
        "reception.model": "Model",
        "reception.vin": "Broj šasije (VIN - 17 znakova)",
        "reception.damage_section": "3. Zapisnik oštećenja karoserije",
        "reception.damage_type": "Tip oštećenja",
        "reception.damage_desc": "Bliži opis",
        "reception.request_section": "4. Zahtev klijenta & Prijem",
        "reception.mileage": "Kilometraža (km)",
        "reception.fuel": "Nivo goriva",
        "reception.complaint": "Opis kvara",
        "reception.photo_url": "Slika (URL)",
        "reception.submit": "Kreiraj Radni Nalog",

        // Orders
        "orders.filter_all": "Svi nalozi",
        "orders.filter_received": "Prijem",
        "orders.filter_in_progress": "U radu",
        "orders.filter_completed": "Završeno",
        "orders.add_item": "+ Stavka",
        "orders.pdf_sr": "📄 SR",
        "orders.pdf_en": "📄 EN",
        "orders.link": "Link",
        "orders.whatsapp": "📱 WA",
        "orders.status_label": "Status popravke:",
        "orders.mileage": "Kilometraža",
        "orders.fuel": "Gorivo",
        "orders.total": "Račun do sada",

        // Dashboard
        "dashboard.monthly_revenue": "Prihod ovog meseca",
        "dashboard.avg_ticket": "Prosečan račun (AOV)",
        "dashboard.active_orders": "Trenutno u radu",
        "dashboard.all_time": "Ukupan promet servisa",
        "dashboard.revenue_structure": "Struktura prihoda",
        "dashboard.labor": "Rad",
        "dashboard.parts": "Delovi",
        "dashboard.top_makes": "Najčešći modeli u servisu",
        "dashboard.mechanics": "Učinak majstora",
        "dashboard.monthly_chart": "Prihod po mesecima",
        "dashboard.status_chart": "Statusi naloga",
        "dashboard.top_parts_chart": "Top 5 najprodavanijih delova",
        "dashboard.mechanics_chart": "Prihod po majstoru",

        // Inventory
        "inventory.add_section": "+ Unos artikla na stanje",
        "inventory.scan": "📷 Skeniraj kod",
        "inventory.sku": "Šifra artikla / Barkod (SKU)",
        "inventory.name": "Naziv dela",
        "inventory.price": "Prodajna cijena (RSD)",
        "inventory.qty": "Količina za upis",
        "inventory.min": "Kritični minimum",
        "inventory.submit": "Upiši na lager",
        "inventory.stock": "Stanje zaliha",
        "inventory.search": "🔍 Brza pretraga...",

        // Reminders
        "reminders.due_title": "Dospeli podsetnici za danas",
        "reminders.due_desc": "Pokretanjem akcije, sistem proverava sve termine i šalje SMS/email vlasnicima.",
        "reminders.process": "Pošalji sve dospele podsetnike danas",
        "reminders.logs_title": "Dnevnik poslatih poruka",

        // Admin
        "admin.total_shops": "Ukupno servisa",
        "admin.active_shops": "aktivnih",
        "admin.total_users": "Ukupno korisnika",
        "admin.in_all_shops": "u svim servisima",
        "admin.total_orders": "Ukupno naloga",
        "admin.all_time": "svih vremena",
        "admin.plans": "Paketi",
        "admin.registered_shops": "Registrovani servisi",
        "admin.search": "🔍 Pretraga...",
        "admin.edit_sub": "⚙️ Izmeni pretplatu",
        "admin.deactivate": "🚫 Deaktiviraj",
        "admin.activate": "✅ Aktiviraj",
        "admin.export": "📥 Export podataka",
        "admin.export_customers": "📥 Klijenti (CSV)",
        "admin.export_vehicles": "📥 Vozila (CSV)",
        "admin.export_orders": "📥 Radni nalozi (CSV)",
        "admin.export_parts": "📥 Magacin (CSV)",

        // Common
        "common.save": "Sačuvaj",
        "common.cancel": "Otkaži",
        "common.delete": "Obriši",
        "common.edit": "Izmeni",
        "common.close": "Zatvori",
        "common.loading": "Učitavanje...",
        "common.no_data": "Nema podataka.",
        "common.success": "Uspešno!",
        "common.error": "Greška!",
    },
    en: {
        // Navigation
        "nav.reception": "Vehicle Reception",
        "nav.orders": "Work Orders",
        "nav.dashboard": "Dashboard",
        "nav.inventory": "Inventory",
        "nav.reminders": "SMS Reminders",
        "nav.admin": "Admin",

        // Header
        "header.logout": "Logout",
        "header.help": "Help",
        "header.guide": "Guide",
        "header.language": "Language",

        // Login
        "login.title": "Welcome back",
        "login.subtitle": "Sign in to your ServisMasterOS account",
        "login.email": "Email address",
        "login.password": "Password",
        "login.submit": "Sign in",
        "login.no_account": "Don't have an account?",
        "login.register_link": "Register your shop",

        // Register
        "register.title": "Register your shop",
        "register.subtitle": "Create an account for your workshop in 30 seconds",
        "register.shop_section": "Shop information",
        "register.shop_name": "Shop name",
        "register.shop_phone": "Shop phone",
        "register.shop_city": "City",
        "register.owner_section": "Owner information",
        "register.owner_name": "Full name",
        "register.owner_email": "Email address (for login)",
        "register.owner_password": "Password (min. 6 characters)",
        "register.submit": "Register shop",
        "register.have_account": "Already have an account?",
        "register.login_link": "Sign in",

        // Reception
        "reception.customer_section": "1. Owner information",
        "reception.customer_search": "Search existing customer",
        "reception.customer_name": "Full name",
        "reception.customer_phone": "Phone (for SMS)",
        "reception.vehicle_section": "2. Vehicle",
        "reception.ocr_title": "Smart registration certificate reader",
        "reception.ocr_camera": "Live Camera",
        "reception.ocr_file": "Choose Image",
        "reception.ocr_manual": "Manual input",
        "reception.plate": "License plate",
        "reception.make": "Make",
        "reception.model": "Model",
        "reception.vin": "VIN (17 characters)",
        "reception.damage_section": "3. Damage report",
        "reception.damage_type": "Damage type",
        "reception.damage_desc": "Description",
        "reception.request_section": "4. Customer request & Reception",
        "reception.mileage": "Mileage (km)",
        "reception.fuel": "Fuel level",
        "reception.complaint": "Complaint description",
        "reception.photo_url": "Photo (URL)",
        "reception.submit": "Create Work Order",

        // Orders
        "orders.filter_all": "All orders",
        "orders.filter_received": "Received",
        "orders.filter_in_progress": "In progress",
        "orders.filter_completed": "Completed",
        "orders.add_item": "+ Item",
        "orders.pdf_sr": "📄 SR",
        "orders.pdf_en": "📄 EN",
        "orders.link": "Link",
        "orders.whatsapp": "📱 WA",
        "orders.status_label": "Repair status:",
        "orders.mileage": "Mileage",
        "orders.fuel": "Fuel",
        "orders.total": "Total so far",

        // Dashboard
        "dashboard.monthly_revenue": "Monthly revenue",
        "dashboard.avg_ticket": "Average ticket (AOV)",
        "dashboard.active_orders": "Currently in progress",
        "dashboard.all_time": "All-time revenue",
        "dashboard.revenue_structure": "Revenue structure",
        "dashboard.labor": "Labor",
        "dashboard.parts": "Parts",
        "dashboard.top_makes": "Most frequent models",
        "dashboard.mechanics": "Mechanic performance",
        "dashboard.monthly_chart": "Revenue by month",
        "dashboard.status_chart": "Order statuses",
        "dashboard.top_parts_chart": "Top 5 parts sold",
        "dashboard.mechanics_chart": "Revenue by mechanic",

        // Inventory
        "inventory.add_section": "+ Add item to stock",
        "inventory.scan": "📷 Scan code",
        "inventory.sku": "SKU / Barcode",
        "inventory.name": "Part name",
        "inventory.price": "Selling price (RSD)",
        "inventory.qty": "Quantity",
        "inventory.min": "Critical minimum",
        "inventory.submit": "Add to stock",
        "inventory.stock": "Stock levels",
        "inventory.search": "🔍 Quick search...",

        // Reminders
        "reminders.due_title": "Due reminders for today",
        "reminders.due_desc": "System checks all appointments and sends SMS/email to owners.",
        "reminders.process": "Send all due reminders today",
        "reminders.logs_title": "Message log",

        // Admin
        "admin.total_shops": "Total shops",
        "admin.active_shops": "active",
        "admin.total_users": "Total users",
        "admin.in_all_shops": "across all shops",
        "admin.total_orders": "Total orders",
        "admin.all_time": "all time",
        "admin.plans": "Plans",
        "admin.registered_shops": "Registered shops",
        "admin.search": "🔍 Search...",
        "admin.edit_sub": "⚙️ Edit subscription",
        "admin.deactivate": "🚫 Deactivate",
        "admin.activate": "✅ Activate",
        "admin.export": "📥 Export data",
        "admin.export_customers": "📥 Customers (CSV)",
        "admin.export_vehicles": "📥 Vehicles (CSV)",
        "admin.export_orders": "📥 Work Orders (CSV)",
        "admin.export_parts": "📥 Inventory (CSV)",

        // Common
        "common.save": "Save",
        "common.cancel": "Cancel",
        "common.delete": "Delete",
        "common.edit": "Edit",
        "common.close": "Close",
        "common.loading": "Loading...",
        "common.no_data": "No data.",
        "common.success": "Success!",
        "common.error": "Error!",
    }
};

const I18n = {
    currentLang: localStorage.getItem("lang") || "sr",

    t(key) {
        return TRANSLATIONS[this.currentLang]?.[key] || TRANSLATIONS["sr"][key] || key;
    },

    setLang(lang) {
        if (!TRANSLATIONS[lang]) return;
        this.currentLang = lang;
        localStorage.setItem("lang", lang);
        this.translatePage();
        this.updateLangButton();
    },

    toggleLang() {
        this.setLang(this.currentLang === "sr" ? "en" : "sr");
    },

    translatePage() {
        // Prevedi elemente sa data-i18n
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            const translation = this.t(key);
            if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
                el.placeholder = translation;
            } else {
                el.textContent = translation;
            }
        });

        // Prevedi elemente sa data-i18n-placeholder
        document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
            const key = el.getAttribute("data-i18n-placeholder");
            el.placeholder = this.t(key);
        });
    },

    updateLangButton() {
        const btn = document.getElementById("btn-lang");
        if (btn) {
            btn.textContent = this.currentLang === "sr" ? "🇷🇸 SR" : "🇬🇧 EN";
        }
    },

    addLangButton() {
        const header = document.querySelector("header");
        if (!header || document.getElementById("btn-lang")) return;

        const btn = document.createElement("button");
        btn.id = "btn-lang";
        btn.className = "btn-secondary header-logout-btn";
        btn.style.marginRight = "8px";
        btn.textContent = this.currentLang === "sr" ? "🇷🇸 SR" : "🇬🇧 EN";
        btn.title = "Promeni jezik / Change language";

        btn.addEventListener("click", () => this.toggleLang());

        // Ubaci pre logout dugmeta
        const logoutBtn = header.querySelector("#btn-logout");
        if (logoutBtn) {
            header.insertBefore(btn, logoutBtn);
        } else {
            header.appendChild(btn);
        }
    }
};

document.addEventListener("DOMContentLoaded", () => {
    I18n.addLangButton();
    I18n.translatePage();
});

// Eksportuj za korišćenje u drugim fajlovima
window.I18n = I18n;