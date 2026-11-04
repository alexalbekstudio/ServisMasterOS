document.addEventListener("DOMContentLoaded", async () => {
    const ordersList = document.getElementById("orders-list");
    const filterBtns = document.querySelectorAll(".filter-btn");
    const alertBox = document.getElementById("alert-box");
    const btnLogout = document.getElementById("btn-logout");

    const itemModal = document.getElementById("item-modal");
    const aiModal = document.getElementById("ai-modal");
    const assistantModal = document.getElementById("assistant-modal");

    let currentFilter = "ALL";
    let allOrders = [];
    let itemScanner = null;

    // =====================================================
    // 1. PRIKAZ NALOGA
    // =====================================================
    async function loadOrders() {
        try {
            const res = await fetch("/api/v1/work-orders/", {
                headers: ApiService.getHeaders()
            });
            if (!res.ok) throw new Error("Neuspešno preuzimanje naloga");
            allOrders = await res.json();
            renderOrders();
        } catch (e) {
            ordersList.innerHTML = `<div class="card error-state-card">${e.message}</div>`;
        }
    }

    function renderOrders() {
        const filtered = allOrders.filter(o => currentFilter === "ALL" || o.status === currentFilter);

        if (filtered.length === 0) {
            ordersList.innerHTML = `<div class="card empty-state-card">Nema naloga za izabrani status.</div>`;
            return;
        }

        ordersList.innerHTML = "";
        filtered.forEach(o => {
            const card = document.createElement("div");
            card.className = "card order-card";
            const total = parseFloat(o.total_amount || 0).toLocaleString("sr-RS", { minimumFractionDigits: 2 });

            card.innerHTML = `
                <div class="order-card-header">
                    <div>
                        <span class="badge">#${o.order_number}</span>
                        <span style="font-weight: 700; margin-left: 6px;">${o.vehicle ? `${o.vehicle.make} ${o.vehicle.model}` : 'Vozilo'}</span>
                    </div>
                    <span class="plate-tag">${o.vehicle ? o.vehicle.license_plate : 'N/A'}</span>
                </div>
                <div class="order-meta-info">
                    <div>Kilometraža: <strong>${o.mileage_at_reception.toLocaleString()} km</strong> | Gorivo: ${o.fuel_level}</div>
                    <div class="order-complaint-row">${o.complaint_description || 'Nema opisa'}</div>
                    <div class="order-total-row">Račun do sada: <strong class="order-total-accent">${total} RSD</strong></div>
                </div>
                <div>
                    <label class="status-label">Status popravke:</label>
                    <select class="status-select-inline" data-id="${o.id}">
                        <option value="RECEIVED" ${o.status === 'RECEIVED' ? 'selected' : ''}>Prijem</option>
                        <option value="DIAGNOSING" ${o.status === 'DIAGNOSING' ? 'selected' : ''}>Dijagnostika</option>
                        <option value="WAITING_FOR_PARTS" ${o.status === 'WAITING_FOR_PARTS' ? 'selected' : ''}>Čeka delove</option>
                        <option value="IN_PROGRESS" ${o.status === 'IN_PROGRESS' ? 'selected' : ''}>U radu</option>
                        <option value="COMPLETED" ${o.status === 'COMPLETED' ? 'selected' : ''}>Završeno</option>
                        <option value="DELIVERED" ${o.status === 'DELIVERED' ? 'selected' : ''}>Preuzeto</option>
                    </select>
                </div>
                <div class="order-actions-row" style="grid-template-columns: 1fr 1fr 1fr;">
                    <button type="button" class="btn-secondary btn-add-item" data-id="${o.id}">+ Stavka</button>
                    <button type="button" class="btn-secondary btn-ai-diagnose" data-id="${o.id}">🤖 AI</button>
                    <button type="button" class="btn-secondary btn-open-pdf" data-id="${o.id}">📄 PDF</button>
                    <button type="button" class="btn-secondary" onclick="window.open('/status?token=${o.tracking_token}', '_blank')">Link</button>
                    <button type="button" class="btn-secondary btn-whatsapp" data-id="${o.id}">📱 WA</button>
                </div>
            `;
            ordersList.appendChild(card);
        });

        // Event listeneri
        document.querySelectorAll(".btn-ai-diagnose").forEach(btn => {
            btn.addEventListener("click", () => {
                const orderId = btn.getAttribute("data-id");
                const order = allOrders.find(o => o.id === orderId);
                document.getElementById("ai-symptoms").value = order?.complaint_description || "";
                aiModal.setAttribute("data-order-id", orderId);
                aiModal.classList.add("active");
                document.getElementById("ai-symptoms").focus();
            });
        });

        document.querySelectorAll(".status-select-inline").forEach(sel => {
            sel.addEventListener("change", async (e) => {
                const orderId = e.target.getAttribute("data-id");
                try {
                    const res = await fetch(`/api/v1/work-orders/${orderId}`, {
                        method: "PATCH",
                        headers: ApiService.getHeaders(),
                        body: JSON.stringify({ status: e.target.value })
                    });
                    if (!res.ok) throw new Error("Greška.");
                    showAlert("Status ažuriran", "success");
                    loadOrders();
                } catch (err) { showAlert(err.message, "error"); }
            });
        });

        document.querySelectorAll(".btn-add-item").forEach(btn => {
            btn.addEventListener("click", () => {
                document.getElementById("modal-order-id").value = btn.getAttribute("data-id");
                document.getElementById("modal-item-title").value = "";
                document.getElementById("modal-item-price").value = "";
                document.getElementById("modal-item-qty").value = "1.0";
                document.getElementById("modal-item-is-part").value = "true";
                document.getElementById("modal-item-requires-approval").checked = false;
                itemModal.classList.add("active");
            });
        });

        document.querySelectorAll(".btn-open-pdf").forEach(btn => {
            btn.addEventListener("click", async () => {
                const orderId = btn.getAttribute("data-id");
                btn.textContent = "⏳...";
                try {
                    const res = await fetch(`/api/v1/work-orders/${orderId}/pdf`, {
                        headers: ApiService.getHeaders()
                    });
                    if (!res.ok) throw new Error("Greška.");
                    const blob = await res.blob();
                    window.open(URL.createObjectURL(blob), "_blank");
                } catch (e) { alert(e.message); }
                finally { btn.textContent = "📄 PDF"; }
            });
        });

        document.querySelectorAll(".btn-whatsapp").forEach(btn => {
            btn.addEventListener("click", async () => {
                const orderId = btn.getAttribute("data-id");
                btn.disabled = true;
                btn.textContent = "⏳";
                try {
                    const res = await fetch(`/api/v1/work-orders/${orderId}/whatsapp-link?message_type=status`, {
                        headers: ApiService.getHeaders()
                    });
                    if (!res.ok) throw new Error("Greška.");
                    const data = await res.json();
                    window.open(data.whatsapp_link, "_blank");
                } catch (e) { showAlert(e.message, "error"); }
                finally { btn.disabled = false; btn.textContent = "📱 WA"; }
            });
        });
    }

    // =====================================================
    // 2. MODAL ZA STAVKU
    // =====================================================
    document.getElementById("btn-close-modal").addEventListener("click", () => {
        stopItemScanner();
        itemModal.classList.remove("active");
    });

    document.getElementById("btn-save-item").addEventListener("click", async () => {
        const orderId = document.getElementById("modal-order-id").value;
        const title = document.getElementById("modal-item-title").value.trim();
        const isPart = document.getElementById("modal-item-is-part").value === "true";
        const qty = parseFloat(document.getElementById("modal-item-qty").value) || 1.0;
        const price = parseFloat(document.getElementById("modal-item-price").value) || 0;
        const requiresApproval = document.getElementById("modal-item-requires-approval").checked;

        if (!title || price <= 0) {
            alert("Unesite naziv i validnu cenu.");
            return;
        }

        try {
            const res = await fetch(`/api/v1/work-orders/${orderId}/items`, {
                method: "POST",
                headers: ApiService.getHeaders(),
                body: JSON.stringify({
                    is_part: isPart, title: title, quantity: qty,
                    unit_price: price, requires_approval: requiresApproval
                })
            });
            if (!res.ok) throw new Error("Neuspešno dodavanje.");
            stopItemScanner();
            itemModal.classList.remove("active");
            showAlert(requiresApproval ? "Stavka dodata i poslat zahtev!" : "Stavka uspešno dodata!", "success");
            loadOrders();
        } catch (err) { alert(err.message); }
    });

    // Skener barkoda u modalu za stavku
    document.getElementById("btn-scan-part-item").addEventListener("click", async () => {
        const scannerBox = document.getElementById("order-item-scanner-box");
        if (scannerBox.style.display === "block") {
            stopItemScanner();
            return;
        }
        scannerBox.style.display = "block";

        try {
            itemScanner = new Html5Qrcode("order-item-reader");
            await itemScanner.start(
                { facingMode: "environment" },
                { fps: 20, qrbox: { width: 260, height: 160 } },
                async (decodedText) => {
                    const barcode = decodedText.trim();
                    stopItemScanner();
                    try {
                        const res = await fetch(`/api/v1/parts/?search=${encodeURIComponent(barcode)}`, {
                            headers: ApiService.getHeaders()
                        });
                        if (res.ok) {
                            const items = await res.json();
                            const found = items.find(i => i.sku === barcode) || items[0];
                            if (found) {
                                document.getElementById("modal-item-title").value = found.name;
                                document.getElementById("modal-item-price").value = found.selling_price;
                                return;
                            }
                        }
                    } catch (err) {}
                    document.getElementById("modal-item-title").value = `Deo [${barcode}]`;
                },
                () => {}
            );
        } catch (err) {
            alert("Kamera nije dostupna.");
            stopItemScanner();
        }
    });

    function stopItemScanner() {
        if (itemScanner) {
            itemScanner.stop().then(() => {
                itemScanner.clear();
                document.getElementById("order-item-scanner-box").style.display = "none";
                itemScanner = null;
            }).catch(() => {
                document.getElementById("order-item-scanner-box").style.display = "none";
            });
        } else {
            document.getElementById("order-item-scanner-box").style.display = "none";
        }
    }

    // =====================================================
    // 3. AI DIJAGNOSTIKA — Kopiraj u clipboard i otvori Gemini
    // =====================================================
    document.getElementById("btn-close-ai").addEventListener("click", () => aiModal.classList.remove("active"));

    document.getElementById("btn-run-ai").addEventListener("click", async () => {
        const symptoms = document.getElementById("ai-symptoms").value.trim();
        if (!symptoms || symptoms.length < 10) {
            showAlert("Unesite najmanje 10 znakova.", "error");
            return;
        }

        const orderId = aiModal.getAttribute("data-order-id");
        const order = allOrders.find(o => o.id === orderId);

        let fullPrompt = `Dijagnostika kvara na vozilu:\n${symptoms}`;
        if (order && order.vehicle) {
            fullPrompt += `\n\nVozilo: ${order.vehicle.make} ${order.vehicle.model} (${order.vehicle.license_plate})`;
        }
        fullPrompt += "\n\nTi si iskusan auto-majstor. Predloži 3-5 mogućih uzroka kvara i preporuke za proveru. Odgovori na srpskom jeziku.";

        try {
            await navigator.clipboard.writeText(fullPrompt);
            showAlert("✅ Pitanje kopirano! Otvaram Gemini...", "success");
        } catch (err) {
            const ta = document.createElement("textarea");
            ta.value = fullPrompt;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand("copy");
            document.body.removeChild(ta);
            showAlert("✅ Pitanje kopirano! Otvaram Gemini...", "success");
        }

        window.open("https://gemini.google.com/app", "_blank");
        aiModal.classList.remove("active");
    });

    // =====================================================
    // 4. AI POMOĆNIK — Kopiraj u clipboard i otvori Gemini
    // =====================================================
    document.getElementById("btn-ai-assistant").addEventListener("click", () => {
        assistantModal.classList.add("active");
        document.getElementById("assistant-question").focus();
    });

    document.getElementById("btn-close-assistant").addEventListener("click", () => assistantModal.classList.remove("active"));

    document.getElementById("btn-ask-assistant").addEventListener("click", async () => {
        const question = document.getElementById("assistant-question").value.trim();
        if (!question) return;

        const vehicleContext = document.getElementById("assistant-vehicle").value.trim();
        let fullPrompt = question;
        if (vehicleContext) fullPrompt += `\n\nKontekst vozila: ${vehicleContext}`;
        fullPrompt += "\n\nOdgovori kao iskusan auto-majstor, na srpskom jeziku.";

        try {
            await navigator.clipboard.writeText(fullPrompt);
            showAlert("✅ Pitanje kopirano! Otvaram Gemini...", "success");
        } catch (err) {
            const ta = document.createElement("textarea");
            ta.value = fullPrompt;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand("copy");
            document.body.removeChild(ta);
        }

        window.open("https://gemini.google.com/app", "_blank");
        assistantModal.classList.remove("active");
        document.getElementById("assistant-question").value = "";
    });

    // =====================================================
    // 5. FILTERI I POMOĆNE
    // =====================================================
    filterBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            filterBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentFilter = btn.getAttribute("data-status");
            renderOrders();
        });
    });

    function showAlert(msg, type) {
        alertBox.textContent = msg;
        alertBox.className = `status-alert ${type}`;
        setTimeout(() => alertBox.className = "status-alert", 5000);
    }

    btnLogout.addEventListener("click", () => {
        localStorage.removeItem("token");
        location.reload();
    });

    loadOrders();
});