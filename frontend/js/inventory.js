document.addEventListener("DOMContentLoaded", async () => {
    const partsList = document.getElementById("parts-list");
    const partSearch = document.getElementById("part-search");
    const btnSave = document.getElementById("btn-save-part");
    const btnOpenScanner = document.getElementById("btn-open-scanner");
    const btnCloseScanner = document.getElementById("btn-close-scanner");
    const scannerModal = document.getElementById("scanner-modal");
    const scannerStatus = document.getElementById("scanner-status");
    const scanFileInput = document.getElementById("scan-file-input");
    const btnLogout = document.getElementById("btn-logout");

    let zxingReader = null;

    // =====================================================
    // 1. UČITAVANJE DELOVA
    // =====================================================
    async function loadParts(search = "") {
        try {
            const url = search ? `/api/v1/parts/?search=${encodeURIComponent(search)}` : "/api/v1/parts/";
            const res = await fetch(url, { headers: ApiService.getHeaders() });
            if (!res.ok) throw new Error("Greška pri učitavanju magacina.");
            const parts = await res.json();

            if (!Array.isArray(parts) || parts.length === 0) {
                partsList.innerHTML = `<div class="empty-state-text">Lager je prazan.</div>`;
                return;
            }

            partsList.innerHTML = "";
            parts.forEach(p => {
                const isLow = p.quantity <= p.min_quantity;
                const div = document.createElement("div");
                div.className = "item-row";
                div.innerHTML = `
                    <div>
                        <div class="item-name">${p.name}</div>
                        <div class="item-meta">${p.sku ? `SKU: ${p.sku} | ` : ''}Cijena: ${parseFloat(p.selling_price).toLocaleString()} RSD</div>
                    </div>
                    <div class="item-right-col">
                        <span class="stock-tag ${isLow ? 'stock-low' : 'stock-ok'}">
                            ${p.quantity} kom ${isLow ? '⚠️ MINIMUM' : ''}
                        </span>
                    </div>
                `;
                partsList.appendChild(div);
            });
        } catch (e) {
            partsList.innerHTML = `<div class="error-state-text">${e.message}</div>`;
        }
    }

    // =====================================================
    // 2. DODAVANJE NA LAGER
    // =====================================================
    btnSave.addEventListener("click", async () => {
        const name = document.getElementById("part-name").value.trim();
        const sku = document.getElementById("part-sku").value.trim();
        const price = parseFloat(document.getElementById("part-selling").value) || 0;
        const qty = parseInt(document.getElementById("part-qty").value) || 0;
        const min = parseInt(document.getElementById("part-min").value) || 2;

        if (!name || price <= 0) {
            alert("Unesite ispravan naziv i cijenu.");
            return;
        }

        try {
            const res = await fetch("/api/v1/parts/", {
                method: "POST",
                headers: ApiService.getHeaders(),
                body: JSON.stringify({
                    name: name, sku: sku, selling_price: price,
                    quantity: qty, min_quantity: min
                })
            });
            if (!res.ok) throw new Error("Greška pri unosu.");
            document.getElementById("part-name").value = "";
            document.getElementById("part-sku").value = "";
            document.getElementById("part-selling").value = "";
            document.getElementById("part-qty").value = "1";
            loadParts();
            showAlert("Deo dodat na lager!", "success");
        } catch (e) { alert(e.message); }
    });

    // =====================================================
    // 3. ZXING SKENER
    // =====================================================
    btnOpenScanner.addEventListener("click", async () => {
        scannerModal.style.display = "flex";
        scannerStatus.textContent = "Aktiviram kameru...";

        try {
            zxingReader = new ZXing.BrowserMultiFormatReader();
            scannerStatus.textContent = "Usmerite kameru na barkod...";

            await zxingReader.decodeFromVideoDevice(
                undefined,
                "reader",
                (result, error) => {
                    if (result) {
                        onScanSuccess(result.getText());
                    }
                }
            );
        } catch (err) {
            console.error("ZXing greška:", err);
            scannerStatus.textContent = "Greška: " + err.message;
        }
    });

    function stopScanner() {
        if (zxingReader) {
            try { zxingReader.reset(); } catch (e) {}
            zxingReader = null;
        }
        scannerModal.style.display = "none";
    }

    btnCloseScanner.addEventListener("click", stopScanner);

    // Upload slike
    scanFileInput.addEventListener("change", async (e) => {
        if (e.target.files.length === 0) return;
        const file = e.target.files[0];
        scannerStatus.textContent = "⏳ Očitavam fajl...";

        try {
            const reader = new ZXing.BrowserMultiFormatReader();
            const result = await reader.decodeFromImageUrl(URL.createObjectURL(file));
            if (result) onScanSuccess(result.getText());
            else alert("Kod nije pronađen na slici.");
        } catch (err) {
            alert("Kod nije pronađen.");
        }
    });

    async function onScanSuccess(decodedText) {
        let scannedCode = decodedText.trim();

        if (scannedCode.includes("purs.gov.rs") || scannedCode.startsWith("http")) {
            try {
                const url = new URL(scannedCode);
                const vl = url.searchParams.get("vl");
                if (vl) scannedCode = vl.slice(0, 24);
            } catch (e) {}
        }

        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            osc.connect(ctx.destination);
            osc.frequency.value = 880;
            osc.start();
            osc.stop(ctx.currentTime + 0.15);
        } catch (e) {}

        stopScanner();
        document.getElementById("part-sku").value = scannedCode;

        try {
            const res = await fetch(`/api/v1/parts/?search=${encodeURIComponent(scannedCode)}`, {
                headers: ApiService.getHeaders()
            });
            if (res.ok) {
                const items = await res.json();
                const existing = items.find(i => i.sku === scannedCode);
                if (existing) {
                    document.getElementById("part-name").value = existing.name;
                    document.getElementById("part-selling").value = existing.selling_price;
                    document.getElementById("part-min").value = existing.min_quantity;
                    alert(`Pronađen artikl: "${existing.name}"\nNa lageru: ${existing.quantity} kom.`);
                    document.getElementById("part-qty").focus();
                    return;
                }
            }
        } catch (e) {}

        document.getElementById("part-name").focus();
    }

    // Pretraga
    partSearch.addEventListener("input", (e) => loadParts(e.target.value));

    btnLogout.addEventListener("click", () => {
        localStorage.removeItem("token");
        location.reload();
    });

    function showAlert(msg, type) {
        // Jednostavan alert jer inventory.html nema status-alert
        console.log(`[${type}] ${msg}`);
    }

    loadParts();
});