# ServisMasterOS — Uputstvo za korišćenje

> Verzija 1.0 · Poslednja izmena: Novembar 2026.

## Sadržaj

1. [Prvi koraci](#1-prvi-koraci)
2. [Prijem vozila](#2-prijem-vozila)
3. [Radni nalozi](#3-radni-nalozi)
4. [Magacin](#4-magacin)
5. [SMS podsetnici](#5-sms-podsetnici)
6. [Kontrolna tabla](#6-kontrolna-tabla)
7. [Klijentski portal](#7-klijentski-portal)
8. [Notifikacije](#8-notifikacije)
9. [PDF dokumenti](#9-pdf-dokumenti)
10. [Česta pitanja](#10-česta-pitanja)

---

## 1. Prvi koraci

### Prijava
1. Otvorite aplikaciju na `http://localhost:8000/login`
2. Unesite email i lozinku
3. Kliknite **„Prijavi se"**

### Registracija novog servisa
1. Otvorite `http://localhost:8000/register`
2. Popunite podatke o servisu (naziv, telefon, grad)
3. Popunite podatke o vlasniku (ime, email, lozinka)
4. Kliknite **„Registruj servis"**

### Odjava
Kliknite **„Odjava"** u gornjem desnom uglu.

---

## 2. Prijem vozila

### Korak 1: Pronađite ili kreirajte klijenta
- Ukucajte deo imena ili telefona u polje za pretragu
- Ako klijent ne postoji, kliknite **„+ Novi klijent"**
- Popunite ime i telefon (obavezno)

### Korak 2: Unesite podatke o vozilu
- **Skenirajte saobraćajnu** (kamera ili slika) — automatski popunjava tablicu, VIN, marku
- **Ili ručno unesite:**
  - Registarska oznaka (npr. PA-123-AA)
  - Marka (npr. Renault)
  - Model (npr. Megane III)
  - VIN (17 znakova — automatski dekodira)

### Korak 3: Označite oštećenja
- Kliknite na dijagram automobila
- Izaberite tip oštećenja (ogrebotina, udubljenje, itd.)
- Dodajte opis (opciono)

### Korak 4: Popunite opis kvara
- **Kilometraža** (obavezno)
- **Nivo goriva**
- **Opis kvara** (što detaljniji, to bolje)

### Korak 5: Kreirajte radni nalog
Kliknite **„Kreiraj Radni Nalog"**. Sistem automatski:
- Generiše broj naloga
- Kreira tracking token za klijenta
- Šalje notifikaciju (Telegram/Email)

---

## 3. Radni nalozi

### Promena statusa
Koristite padajući meni:
- **Prijem** → **Dijagnostika** → **Čeka delove** → **U radu** → **Završeno** → **Preuzeto**

Klijent automatski dobija obaveštenje o svakoj promeni.

### Dodavanje stavki
1. Kliknite **„+ Stavka"**
2. Izaberite tip:
   - **⚙️ Rezervni deo** — razdužuje magacin
   - **🔧 Rad / Usluga** — samo dodaje na račun
3. Unesite naziv, količinu, cenu
4. (Opciono) Štiklirajte **„⚠️ Traži odobrenje"** ako je dodatni rad

### PDF dokumenti
- **📄 SR** — PDF radni nalog na srpskom
- **📄 EN** — PDF radni nalog na engleskom

### Deljenje sa klijentom
Kliknite **„Link"** da kopirate link za praćenje statusa.
Pošaljite link klijentu putem SMS-a, WhatsApp-a ili email-a.

---

## 4. Magacin

### Dodavanje artikla
1. Otvorite `/inventory`
2. Kliknite **„📷 Skeniraj kod"** ili ručno unesite:
   - Šifra (SKU)
   - Naziv
   - Prodajna cena
   - Količina
   - Kritični minimum
3. Kliknite **„Upiši na lager"**

### Praćenje zaliha
- **Zelena oznaka** — dovoljno na lageru
- **Crvena oznaka (⚠️ MINIMUM)** — ispod minimuma, treba naručiti

### Automatsko razduživanje
Kada dodate deo na radni nalog, magacin se **automatski razdužuje**.
Sve promene se beleže u `inventory_logs` (revizorski trag).

---

## 5. SMS podsetnici

### Automatski podsetnici
Sistem automatski prati:
- **Istek registracije** — 15 dana pre isteka
- **Redovan mali servis** — na osnovu kilometraže ili 12 meseci

### Slanje podsetnika
1. Otvorite `/reminders`
2. Kliknite **„Pošalji sve dospele podsetnike danas"**
3. Sistem šalje SMS/Email/Telegram svim klijentima sa dospelim podsetnikom

### Dnevnik poruka
Prikazuje sve poslate poruke sa statusom isporuke.

---

## 6. Kontrolna tabla

### KPI kartice
- **Prihod ovog meseca** — suma svih završenih naloga
- **Prosečan račun (AOV)** — prihod / broj naloga
- **Trenutno u radu** — broj aktivnih naloga
- **Ukupan promet** — kumulativno

### Struktura prihoda
Vizuelno prikazuje odnos **rada** (plavo) i **delova** (narandžasto).

### Učinak majstora
Rang lista majstora po prihodu. Možete filtrirati po periodu (7, 30, 90 dana).

---

## 7. Klijentski portal

### Praćenje statusa
Klijent otvara link: `http://localhost:8000/status?token=...`
Vidi:
- Trenutni status (6 koraka)
- Vremensku liniju promena
- Stavke (radovi + delovi)
- Ukupan iznos
- IPS QR kod za plaćanje
- Foto-dokumentaciju

### Odobrenje dodatnih radova
Ako majstor doda stavku sa **„⚠️ Traži odobrenje"**, klijent vidi:
- Naziv stavke
- Cenu
- Dugmad **„✓ Odobravam"** i **„✕ Odbijam"**

---

## 8. Notifikacije

### Telegram
- Automatski šalje poruke pri:
  - Prijemu vozila
  - Promeni statusa
  - Završetku
  - Zahtevu za odobrenje

### Email
- Automatski šalje email pri:
  - Prijemu vozila
  - Završetku (sa PDF računom)
  - Podsetnicima

### WhatsApp
- Klik na **„📱 WA"** otvara WhatsApp sa pripremljenom porukom
- Majstor samo klikne „Pošalji" u WhatsApp-u

---

## 9. PDF dokumenti

### Radni nalog (SR)
Klik na **„📄 SR"** u `/orders` — generiše PDF sa:
- Logom servisa
- Podacima o servisu, klijentu, vozilu
- Tabelom stavki
- IPS QR kodom za plaćanje
- Potpisima

### Radni nalog (EN)
Klik na **„📄 EN"** — isti PDF na engleskom jeziku.

### Fiskalni račun
Kada je nalog završen, klik na **„📄 Fiskalni"** (ako je omogućeno) — generiše fiskalni račun.

---

## 10. Česta pitanja

### Kako da promenim lozinku?
Trenutno nije omogućeno kroz UI. Kontaktirajte administratora.

### Kako da dodam novog korisnika (majstora)?
Kontaktirajte administratora (funkcionalnost u razvoju).

### Kako da izvezem podatke?
Trenutno nije omogućeno. Planirano za buduće verzije.

### Kako da promenim paket pretplate?
Kontaktirajte administratora (`alexalbekstudio.design@gmail.com`).

### Zašto ne dobijam notifikacije?
Proverite:
1. Da li je Telegram bot aktivan
2. Da li je email adresa ispravna
3. Da li je klijent uneo ispravan telefon/email

---

## Kontakt

- **Email:** alexalbekstudio.design@gmail.com
- **Web:** https://servismaster.rs (u pripremi)

---

**Hvala što koristite ServisMasterOS!** 🚀