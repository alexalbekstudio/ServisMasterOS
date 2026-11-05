document.addEventListener("DOMContentLoaded", async () => {
    const shopsList = document.getElementById("shops-list");
    const shopSearch = document.getElementById("shop-search");
    const btnLogout = document.getElementById("btn-logout");
    const subModal = document.getElementById("sub-modal");

    let allShops = [];

    // ============================================
    // 1. UČITAVANJE STATISTIKE
    // ============================================
    async function loadStats() {
        try {
            const res = await fetch("/api/v1/admin/stats", {
                headers: ApiService.getHeaders(),
            });
            if (!res.ok) throw new Error("Greška.");
            const data = await res.json();

            document.getElementById("kpi-total-shops").textContent = data.total_shops;
            document.getElementById("kpi-active-shops").textContent = `${data.active_shops} aktivnih`;
            document.getElementById("kpi-total-users").textContent = data.total_users;
            document.getElementById("kpi-total-orders").textContent = data.total_orders;

            const plans = data.plans || {};
            const plansText = Object.entries(plans).map(([k, v]) => `${k}: ${v}`).join(" · ") || "-";
            document.getElementById("kpi-plans").textContent = plansText;
        } catch (e) {
            console.error("Stats greška:", e);
        }
    }

    // ============================================
    // 2. UČITAVANJE SERVISA
    // ============================================
    async function loadShops(search = "") {
        try {
            const res = await fetch("/api/v1/admin/shops", {
                headers: ApiService.getHeaders(),
            });
            if (!res.ok) {
                if (res.status === 403) {
                    shopsList.innerHTML = `<div class="error-state-text">Pristup odbijen. Samo super-admin može da pristupi.</div>`;
                    return;
                }
                throw new Error("Greška.");
            }
            allShops = await res.json();
            renderShops(search);
        } catch (e) {
            shopsList.innerHTML = `<div class="error-state-text">${e.message}</div>`;
        }
    }

    function renderShops(search = "") {
        const filtered = allShops.filter(s => {
            if (!search) return true;
            const q = search.toLowerCase();
            return (s.shop_name || "").toLowerCase().includes(q) ||
                   (s.shop_city || "").toLowerCase().includes(q) ||
                   (s.owner_email || "").toLowerCase().includes(q);
        });

        if (filtered.length === 0) {
            shopsList.innerHTML = `<div class="empty-state-text">Nema servisa.</div>`;
            return;
        }

        shopsList.innerHTML = "";
        filtered.forEach(s => {
            const row = document.createElement("div");
            row.className = "item-row";
            row.style.cssText = "display: block; padding: 14px 0; border-bottom: 1px solid var(--card-border);";
            
            const sub = s.subscription;
            const planBadgeColor = {
                BASIC: "var(--gray-400)",
                PRO: "var(--accent)",
                ENTERPRISE: "var(--success)",
            }[sub?.plan] || "var(--gray-400)";
            
            const statusBadge = {
                TRIAL: "🧪 Trial",
                ACTIVE: "✅ Aktivan",
                SUSPENDED: "⏸️ Suspendovan",
                CANCELLED: "❌ Otkazan",
            }[sub?.status] || "-";

            row.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 200px;">
                        <div style="font-weight: 700; font-size: 1rem; margin-bottom: 4px;">
                            ${escapeHtml(s.shop_name)}
                            ${!s.is_active ? '<span style="color: var(--danger); font-size: 0.75rem;"> (DEAKTIVIRAN)</span>' : ''}
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">
                            ${escapeHtml(s.shop_city || '')} · ${escapeHtml(s.shop_phone || '')}
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">
                            👤 ${escapeHtml(s.owner_name || 'N/A')} (${escapeHtml(s.owner_email || 'N/A')})
                        </div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">
                            👥 ${s.users_count} korisnika · 📋 ${s.orders_count} naloga
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: ${planBadgeColor}; margin-bottom: 4px;">
                            ${sub?.plan || 'Nema paket'}
                        </div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px;">
                            ${statusBadge}
                        </div>
                        <button type="button" class="btn-secondary btn-edit-sub" data-id="${s.shop_id}" style="width: auto; padding: 6px 12px; font-size: 0.8rem; margin: 0;">
                            ⚙️ Izmeni pretplatu
                        </button>
                        <button type="button" class="btn-secondary btn-toggle-active" data-id="${s.shop_id}" style="width: auto; padding: 6px 12px; font-size: 0.8rem; margin: 4px 0 0 0;">
                            ${s.is_active ? '🚫 Deaktiviraj' : '✅ Aktiviraj'}
                        </button>
                    </div>
                </div>
            `;
            shopsList.appendChild(row);
        });

        // Event listeneri
        document.querySelectorAll(".btn-edit-sub").forEach(btn => {
            btn.addEventListener("click", () => {
                const shopId = btn.getAttribute("data-id");
                const shop = allShops.find(s => s.shop_id === shopId);
                if (!shop) return;

                document.getElementById("sub-shop-id").value = shopId;
                document.getElementById("sub-modal-title").textContent = `Izmena pretplate: ${shop.shop_name}`;
                
                const sub = shop.subscription || {};
                document.getElementById("sub-plan").value = sub.plan || "BASIC";
                document.getElementById("sub-status").value = sub.status || "TRIAL";
                document.getElementById("sub-max-users").value = sub.max_users || 1;
                document.getElementById("sub-max-orders").value = sub.max_work_orders_per_month || 50;
                document.getElementById("sub-notes").value = "";

                subModal.classList.add("active");
            });
        });

        document.querySelectorAll(".btn-toggle-active").forEach(btn => {
            btn.addEventListener("click", async () => {
                const shopId = btn.getAttribute("data-id");
                if (!confirm("Da li ste sigurni da želite da promenite status servisa?")) return;
                
                try {
                    const res = await fetch(`/api/v1/admin/shops/${shopId}/toggle-active`, {
                        method: "PATCH",
                        headers: ApiService.getHeaders(),
                    });
                    if (!res.ok) throw new Error("Greška.");
                    loadShops();
                    loadStats();
                } catch (e) {
                    alert(e.message);
                }
            });
        });
    }

    // ============================================
    // 3. MODAL ZA PRETPLATU
    // ============================================
    document.getElementById("btn-close-sub").addEventListener("click", () => {
        subModal.classList.remove("active");
    });

    document.getElementById("btn-save-sub").addEventListener("click", async () => {
        const shopId = document.getElementById("sub-shop-id").value;
        const plan = document.getElementById("sub-plan").value;
        const status = document.getElementById("sub-status").value;
        const maxUsers = parseInt(document.getElementById("sub-max-users").value) || 1;
        const maxOrders = parseInt(document.getElementById("sub-max-orders").value) || 50;
        const notes = document.getElementById("sub-notes").value.trim();

        try {
            const res = await fetch(`/api/v1/admin/shops/${shopId}/subscription`, {
                method: "PATCH",
                headers: ApiService.getHeaders(),
                body: JSON.stringify({
                    plan: plan,
                    status: status,
                    max_users: maxUsers,
                    max_work_orders_per_month: maxOrders,
                    notes: notes || null,
                }),
            });
            if (!res.ok) throw new Error("Greška.");
            subModal.classList.remove("active");
            loadShops();
            loadStats();
        } catch (e) {
            alert(e.message);
        }
    });

    // ============================================
    // 4. PRETRAGA
    // ============================================
    shopSearch.addEventListener("input", (e) => {
        renderShops(e.target.value);
    });

    // ============================================
    // 5. ODJAVA
    // ============================================
    btnLogout.addEventListener("click", () => {
        ApiService.logout();
    });

    // ============================================
    // 6. POMOĆNE
    // ============================================
    function escapeHtml(str) {
        if (!str) return "";
        return String(str).replace(/[&<>"']/g, s => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
        }[s] || s));
    }

    // ============================================
    // EXPORT PODATAKA
    // ============================================
    async function downloadCsv(url, filename) {
        try {
            const res = await fetch(url, {
                headers: ApiService.getHeaders(),
            });
            if (!res.ok) throw new Error("Greška pri exportu.");

            const blob = await res.blob();
            const fileUrl = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = fileUrl;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(fileUrl);
        } catch (e) {
            alert(e.message);
        }
    }

    document.getElementById("export-customers").addEventListener("click", () => {
        downloadCsv("/api/v1/customers/export/csv", "klijenti.csv");
    });

    document.getElementById("export-vehicles").addEventListener("click", () => {
        downloadCsv("/api/v1/vehicles/export/csv", "vozila.csv");
    });

    document.getElementById("export-orders").addEventListener("click", () => {
        downloadCsv("/api/v1/work-orders/export/csv", "radni_nalozi.csv");
    });

    document.getElementById("export-parts").addEventListener("click", () => {
        downloadCsv("/api/v1/parts/export/csv", "magacin.csv");
    });

    // Init
    loadStats();
    loadShops();
});