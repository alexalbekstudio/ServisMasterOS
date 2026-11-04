document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token");

    const loadingElem = document.getElementById("status-loading");
    const contentElem = document.getElementById("status-content");

    if (!token) {
        loadingElem.textContent = "Nevažeći link za praćenje naloga.";
        loadingElem.style.color = "var(--danger)";
        return;
    }

    async function loadOrderStatus() {
        try {
            const res = await fetch(`/api/v1/work-orders/public/status/${token}`);
            if (!res.ok) throw new Error("Radni nalog nije pronađen.");
            const order = await res.json();

            renderOrderDetails(order);
            loadingElem.style.display = "none";
            contentElem.style.display = "block";
        } catch (err) {
            loadingElem.textContent = err.message;
            loadingElem.style.color = "var(--danger)";
        }
    }

    function renderOrderDetails(order) {
        document.getElementById("order-badge").textContent = `Nalog #${order.order_number}`;
        document.getElementById("vehicle-title").textContent = `${order.vehicle_make} ${order.vehicle_model}`;
        document.getElementById("vehicle-plate").textContent = order.vehicle_plate;
        document.getElementById("complaint-text").textContent = order.complaint_description || "Redovan servis";

        document.getElementById("date-received").textContent = formatDate(order.received_at);
        document.getElementById("date-completed").textContent = order.completed_at ? formatDate(order.completed_at) : "U toku";

        updateStatusTracker(order.status);
        renderTimeline(order.status_history || [], order.status);

        // Odobrenja
        const approvalSection = document.getElementById("approval-section");
        const approvalContainer = document.getElementById("approval-items-container");
        approvalContainer.innerHTML = "";

        const pendingItems = (order.items || []).filter(it => it.requires_approval && it.is_approved === null);

        if (pendingItems.length > 0) {
            approvalSection.style.display = "block";
            pendingItems.forEach(item => {
                const row = document.createElement("div");
                row.className = "approval-item-row";
                row.innerHTML = `
                    <div class="approval-item-header">
                        <span>${item.is_part ? "⚙️" : "🔧"} ${escapeHtml(item.title)}</span>
                        <span class="approval-item-price">${formatCurrency(item.total_price || item.unit_price)}</span>
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">Količina: ${item.quantity} kom</div>
                    <div class="approval-buttons-group">
                        <button type="button" class="btn-approve" data-id="${item.id}">✓ Odobravam</button>
                        <button type="button" class="btn-reject" data-id="${item.id}">✕ Odbijam</button>
                    </div>
                `;
                approvalContainer.appendChild(row);
            });

            approvalContainer.querySelectorAll(".btn-approve").forEach(btn => {
                btn.addEventListener("click", () => handleApproval(btn.getAttribute("data-id"), true));
            });
            approvalContainer.querySelectorAll(".btn-reject").forEach(btn => {
                btn.addEventListener("click", () => handleApproval(btn.getAttribute("data-id"), false));
            });
        } else {
            approvalSection.style.display = "none";
        }

        // Lista stavki
        const itemsList = document.getElementById("items-list");
        itemsList.innerHTML = "";
        const approvedItems = (order.items || []).filter(it => !it.requires_approval || it.is_approved === true);
        if (approvedItems.length === 0) {
            itemsList.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem;">Defektaža u toku.</div>`;
        } else {
            approvedItems.forEach(it => {
                const div = document.createElement("div");
                div.className = "status-item-line";
                div.innerHTML = `
                    <span>${it.is_part ? "⚙️" : "🔧"} ${escapeHtml(it.title)} (${it.quantity} kom)</span>
                    <strong>${formatCurrency(it.total_price)}</strong>
                `;
                itemsList.appendChild(div);
            });
        }

        document.getElementById("total-amount").textContent = formatCurrency(order.total_amount);

        // IPS QR
        const ipsCard = document.getElementById("ips-qr-card");
        const ipsImage = document.getElementById("ips-qr-image");
        if (ipsCard && ipsImage) {
            if (order.payment_qr_base64) {
                ipsImage.src = order.payment_qr_base64;
                ipsCard.style.display = "block";
            } else {
                ipsCard.style.display = "none";
            }
        }

        // Fotografije
        const photosSection = document.getElementById("photos-section");
        const photosGrid = document.getElementById("photos-grid");
        photosGrid.innerHTML = "";
        if (order.photos && order.photos.length > 0) {
            photosSection.style.display = "block";
            order.photos.forEach(ph => {
                const img = document.createElement("img");
                img.className = "photo-thumb";
                img.src = ph.photo_url;
                img.alt = ph.description || "Foto";
                img.onclick = () => window.open(ph.photo_url, "_blank");
                photosGrid.appendChild(img);
            });
        } else {
            photosSection.style.display = "none";
        }
    }

    function updateStatusTracker(status) {
        const badge = document.getElementById("current-status-badge");
        const STEPS = ["RECEIVED", "DIAGNOSING", "WAITING_FOR_PARTS", "IN_PROGRESS", "COMPLETED", "DELIVERED"];
        const LABELS = {
            "RECEIVED": "Primljeno", "DIAGNOSING": "Dijagnostika",
            "WAITING_FOR_PARTS": "Čeka delove", "IN_PROGRESS": "U radu",
            "COMPLETED": "Spremno", "DELIVERED": "Preuzeto", "CANCELLED": "Otkazano",
        };

        STEPS.forEach(s => {
            const el = document.getElementById(`step-${s}`);
            if (el) el.className = "step-item";
        });
        ["1", "2", "3", "4", "5"].forEach(n => {
            const line = document.getElementById(`line-${n}`);
            if (line) line.className = "step-line";
        });

        badge.textContent = LABELS[status] || status;

        let currentIdx = STEPS.indexOf(status);
        if (currentIdx === -1) return;

        STEPS.forEach((s, idx) => {
            const el = document.getElementById(`step-${s}`);
            if (!el) return;
            if (idx < currentIdx) el.classList.add("completed");
            else if (idx === currentIdx) el.classList.add("active");
        });

        for (let i = 0; i < currentIdx; i++) {
            const line = document.getElementById(`line-${i + 1}`);
            if (line) line.classList.add("active");
        }
    }

    function renderTimeline(history, currentStatus) {
        const section = document.getElementById("timeline-section");
        const container = document.getElementById("timeline-container");
        const entries = [...history];

        if (!entries.find(e => e.status === "RECEIVED")) {
            entries.unshift({ status: "RECEIVED", created_at: null, note: "Vozilo primljeno" });
        }

        if (entries.length === 0) {
            section.style.display = "none";
            return;
        }

        section.style.display = "block";
        container.innerHTML = "";

        const STATUS_LABELS = {
            "RECEIVED": "📥 Primljeno", "DIAGNOSING": "🔍 Dijagnostika",
            "WAITING_FOR_PARTS": "⏳ Čeka delove", "IN_PROGRESS": "🔧 U radu",
            "COMPLETED": "✅ Završeno", "DELIVERED": "🎉 Preuzeto",
        };

        entries.forEach((entry, idx) => {
            const isCurrent = entry.status === currentStatus;
            const div = document.createElement("div");
            div.className = `timeline-item ${isCurrent ? "active" : ""} ${idx < entries.length - 1 ? "past" : ""}`;

            const label = STATUS_LABELS[entry.status] || entry.status;
            const dateStr = entry.created_at ? formatDate(entry.created_at) : "Prethodno";

            div.innerHTML = `
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div class="timeline-label">${label}</div>
                    <div class="timeline-date">${dateStr}</div>
                </div>
            `;
            container.appendChild(div);
        });
    }

    async function handleApproval(itemId, isApproved) {
        if (!confirm(isApproved ? "Odobravate radove?" : "Odbijate radove?")) return;

        try {
            const res = await fetch(`/api/v1/work-orders/public/approve/${token}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ item_id: itemId, decision: isApproved }),
            });
            if (!res.ok) throw new Error("Neuspešno.");
            alert(isApproved ? "Odobreno!" : "Odbijeno.");
            loadOrderStatus();
        } catch (e) { alert(e.message); }
    }

    function formatDate(isoStr) {
        if (!isoStr) return "-";
        const d = new Date(isoStr);
        return d.toLocaleDateString("sr-RS", {
            day: "2-digit", month: "2-digit", year: "numeric",
            hour: "2-digit", minute: "2-digit"
        });
    }

    function formatCurrency(val) {
        const num = parseFloat(val) || 0;
        return num.toLocaleString("sr-RS", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " RSD";
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str.replace(/[&<>'"]/g, tag =>
            ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }

    loadOrderStatus();
});