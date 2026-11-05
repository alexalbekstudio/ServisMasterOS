/**
 * Help sistem — kontekstualna pomoć + link ka kompletnom uputstvu.
 */

const HELP_CONTENT = {
    "/": {
        title: "Pomoć: Prijem vozila",
        sections: [
            {
                heading: "1. Pronađite ili kreirajte klijenta",
                text: "Ukucajte deo imena ili telefona u polje za pretragu. Ako klijent ne postoji, kliknite na „+ Novi klijent\" i popunite ime i telefon."
            },
            {
                heading: "2. Unesite podatke o vozilu",
                text: "Možete skenirati saobraćajnu dozvolu (kamera ili slika) ili ručno uneti tablicu, marku, model i VIN. Kada unesete VIN, sistem automatski preuzima podatke o vozilu."
            },
            {
                heading: "3. Označite oštećenja",
                text: "Kliknite na dijagram automobila da označite ogrebotine, udubljenja ili druga oštećenja. Ovo je važno za zaštitu od reklamacija."
            },
            {
                heading: "4. Popunite opis kvara",
                text: "Unesite kilometražu, nivo goriva i detaljan opis problema. Što je opis precizniji, majstor će brže reagovati."
            },
            {
                heading: "5. Kreirajte radni nalog",
                text: "Kliknite na „Kreiraj Radni Nalog\". Sistem automatski šalje SMS/Telegram/Email klijentu sa linkom za praćenje statusa."
            }
        ]
    },
    "/orders": {
        title: "Pomoć: Radni nalozi",
        sections: [
            {
                heading: "Upravljanje statusima",
                text: "Koristite padajući meni da promenite status naloga: Prijem → Dijagnostika → Čeka delove → U radu → Završeno → Preuzeto. Klijent automatski dobija obaveštenje o svakoj promeni."
            },
            {
                heading: "Dodavanje stavki",
                text: "Kliknite na „+ Stavka\" da dodate deo ili uslugu na nalog. Možete skenirati barkod sa kutije dela ili ukucati naziv."
            },
            {
                heading: "Traženje odobrenja",
                text: "Ako dodajete dodatni rad koji klijent nije odobrio, štiklirajte „⚠️ Traži odobrenje\". Klijent dobija link gde može da odobri ili odbije rad."
            },
            {
                heading: "PDF i deljenje",
                text: "Kliknite na „📄 SR\" da preuzmete radni nalog na srpskom, ili „📄 EN\" za engleski. Klik na „Link\" kopira link za praćenje statusa koji možete poslati klijentu."
            }
        ]
    },
    "/dashboard": {
        title: "Pomoć: Kontrolna tabla",
        sections: [
            {
                heading: "KPI kartice",
                text: "Prikazuju prihod ovog meseca, prosečan račun, broj aktivnih naloga i ukupan promet servisa."
            },
            {
                heading: "Struktura prihoda",
                text: "Vizuelno prikazuje odnos prihoda od rada (plavo) i delova (narandžasto)."
            },
            {
                heading: "Učinak majstora",
                text: "Prikazuje rang listu majstora po prihodu. Možete filtrirati po periodu (7, 30, 90 dana)."
            }
        ]
    },
    "/inventory": {
        title: "Pomoć: Magacin",
        sections: [
            {
                heading: "Dodavanje artikla",
                text: "Unesite šifru (SKU), naziv, prodajnu cenu i količinu. Kliknite na „Upiši na lager\". Ako artikal već postoji, količina se automatski uvećava."
            },
            {
                heading: "Skeniranje barkoda",
                text: "Kliknite na „📷 Skeniraj kod\" i usmerite kameru na barkod. Sistem automatski popunjava šifru i naziv."
            },
            {
                heading: "Kritični minimum",
                text: "Kada zaliha padne ispod minimuma, artikal se prikazuje crvenom bojom i dobija oznaku „⚠️ MINIMUM\"."
            }
        ]
    },
    "/reminders": {
        title: "Pomoć: SMS Podsetnici",
        sections: [
            {
                heading: "Automatski podsetnici",
                text: "Sistem automatski prati istek registracije i redovan mali servis. Kliknite na „Pošalji sve dospele podsetnike\" da pošaljete sve poruke za danas."
            },
            {
                heading: "Dnevnik poruka",
                text: "Prikazuje sve poslate SMS/Email/Telegram poruke sa statusom isporuke."
            }
        ]
    },
    "/admin": {
        title: "Pomoć: Admin Panel",
        sections: [
            {
                heading: "Upravljanje pretplatnicima",
                text: "Prikazuje sve registrovane servise. Kliknite na „⚙️ Izmeni pretplatu\" da promenite paket (Basic/Pro/Enterprise), status ili limite."
            },
            {
                heading: "Aktivacija/deaktivacija",
                text: "Kliknite na „🚫 Deaktiviraj\" da privremeno onemogućite pristup servisu (npr. zbog neplaćanja)."
            },
            {
                heading: "Statistika",
                text: "KPI kartice prikazuju ukupan broj servisa, korisnika, naloga i raspodelu paketa."
            }
        ]
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector("header");
    if (!header) return;

    // =====================================================
    // 1. DODAJ "UPUTSTVO" DUGME (vodi na /help)
    // =====================================================
    let helpPageBtn = document.getElementById("btn-help-page");
    if (!helpPageBtn) {
        helpPageBtn = document.createElement("button");
        helpPageBtn.id = "btn-help-page";
        helpPageBtn.className = "btn-secondary header-logout-btn";
        helpPageBtn.style.marginRight = "8px";
        helpPageBtn.innerHTML = "📖 Uputstvo";
        helpPageBtn.title = "Otvori kompletan PDF uputstvo";

        helpPageBtn.addEventListener("click", () => {
            window.open("/help", "_blank");
        });

        // Ubaci pre logout dugmeta
        const logoutBtn = header.querySelector("#btn-logout");
        if (logoutBtn) {
            header.insertBefore(helpPageBtn, logoutBtn);
        } else {
            header.appendChild(helpPageBtn);
        }
    }

    // =====================================================
    // 2. DODAJ "POMOĆ" DUGME (modal sa kontekstualnom pomoći)
    // =====================================================
    let helpBtn = document.getElementById("btn-help");
    if (!helpBtn) {
        helpBtn = document.createElement("button");
        helpBtn.id = "btn-help";
        helpBtn.className = "btn-secondary header-logout-btn";
        helpBtn.style.marginRight = "8px";
        helpBtn.innerHTML = "❓ Pomoć";
        helpBtn.title = "Otvori pomoć za ovu stranicu";

        // Ubaci pre "Uputstvo" dugmeta
        if (helpPageBtn) {
            header.insertBefore(helpBtn, helpPageBtn);
        } else {
            const logoutBtn = header.querySelector("#btn-logout");
            if (logoutBtn) {
                header.insertBefore(helpBtn, logoutBtn);
            } else {
                header.appendChild(helpBtn);
            }
        }
    }

    // =====================================================
    // 3. KREIRAJ HELP MODAL (ako ne postoji)
    // =====================================================
    let helpModal = document.getElementById("help-modal");
    if (!helpModal) {
        helpModal = document.createElement("div");
        helpModal.id = "help-modal";
        helpModal.className = "modal-overlay";
        helpModal.innerHTML = `
            <div class="modal-content" style="max-width: 600px; max-height: 85vh;">
                <div class="modal-header">
                    <h2 class="modal-title" id="help-modal-title">Pomoć</h2>
                    <button type="button" class="btn-secondary modal-close-btn" id="btn-close-help">&times;</button>
                </div>
                <div id="help-modal-content" style="font-size: 0.9rem; line-height: 1.6;"></div>
            </div>
        `;
        document.body.appendChild(helpModal);
    }

    // =====================================================
    // 4. OTVORI MODAL NA KLIK
    // =====================================================
    helpBtn.addEventListener("click", () => {
        const path = window.location.pathname;
        const content = HELP_CONTENT[path] || HELP_CONTENT["/"];

        document.getElementById("help-modal-title").textContent = content.title;

        let html = "";
        content.sections.forEach(s => {
            html += `
                <div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--card-border);">
                    <h3 style="font-size: 0.95rem; color: var(--accent); margin-bottom: 6px;">${s.heading}</h3>
                    <p style="color: var(--text-secondary); margin: 0;">${s.text}</p>
                </div>
            `;
        });

        document.getElementById("help-modal-content").innerHTML = html;
        helpModal.classList.add("active");
    });

    // =====================================================
    // 5. ZATVORI MODAL
    // =====================================================
    document.getElementById("btn-close-help").addEventListener("click", () => {
        helpModal.classList.remove("active");
    });

    // Zatvori na klik van modala
    helpModal.addEventListener("click", (e) => {
        if (e.target === helpModal) {
            helpModal.classList.remove("active");
        }
    });
});