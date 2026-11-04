document.addEventListener("DOMContentLoaded", async () => {
    const btnLogout = document.getElementById("btn-logout");

    async function loadAnalytics() {
        try {
            const res = await fetch("/api/v1/analytics/summary", {
                headers: ApiService.getHeaders()
            });
            if (!res.ok) throw new Error("Neuspešno učitavanje analitike.");
            const data = await res.json();

            document.getElementById("kpi-monthly-rev").textContent = formatRSD(data.monthly_revenue);
            document.getElementById("kpi-completed-orders").textContent = `${data.monthly_completed_count} završenih naloga`;
            document.getElementById("kpi-avg-ticket").textContent = formatRSD(data.average_ticket);
            document.getElementById("kpi-active-orders").textContent = data.active_orders_count;
            document.getElementById("kpi-all-time").textContent = formatRSD(data.all_time_revenue);

            const totalLabor = data.total_labor || 0;
            const totalParts = data.total_parts || 0;
            const totalSplit = totalLabor + totalParts;

            let laborPercent = 50, partsPercent = 50;
            if (totalSplit > 0) {
                laborPercent = Math.round((totalLabor / totalSplit) * 100);
                partsPercent = 100 - laborPercent;
            }

            document.getElementById("bar-labor").style.width = `${laborPercent}%`;
            document.getElementById("bar-parts").style.width = `${partsPercent}%`;
            document.getElementById("val-labor").textContent = `${formatRSD(totalLabor)} (${laborPercent}%)`;
            document.getElementById("val-parts").textContent = `${formatRSD(totalParts)} (${partsPercent}%)`;

            const topList = document.getElementById("top-makes-list");
            topList.innerHTML = "";
            if (!data.top_makes || data.top_makes.length === 0) {
                topList.innerHTML = `<div class="empty-state-text">Nema dovoljno podataka.</div>`;
            } else {
                data.top_makes.forEach((tm, i) => {
                    const row = document.createElement("div");
                    row.className = "top-make-row";
                    row.innerHTML = `
                        <span><strong>${i + 1}. ${tm.make || 'Ostalo'}</strong></span>
                        <span class="badge top-make-badge">${tm.count} servisa</span>
                    `;
                    topList.appendChild(row);
                });
            }
        } catch (e) { console.error("Greška:", e); }
    }

    async function loadMechanicsPerformance() {
        const periodSelect = document.getElementById("mechanics-period");
        const days = periodSelect ? periodSelect.value : 30;
        const listContainer = document.getElementById("mechanics-list");

        try {
            const res = await fetch(`/api/v1/analytics/mechanics?period_days=${days}`, {
                headers: ApiService.getHeaders(),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || "Greška pri učitavanju.");
            }

            const data = await res.json();
            console.log("Mechanics data:", data);

            if (!data.mechanics || data.mechanics.length === 0) {
                listContainer.innerHTML = `<div class="empty-state-text">Nema majstora u sistemu.</div>`;
                return;
            }

            listContainer.innerHTML = "";
            data.mechanics.forEach((m, idx) => {
                const row = document.createElement("div");
                row.style.cssText = "padding: 12px 0; border-bottom: 1px solid var(--card-border); display: flex; justify-content: space-between; align-items: center; gap: 12px;";

                row.innerHTML = `
                    <div style="flex: 1;">
                        <div style="font-weight: 700; font-size: 0.9rem;">${escapeHtml(m.mechanic_name)}</div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">
                            <strong>${m.completed_orders}</strong> završenih · <strong>${m.active_orders}</strong> aktivnih · Prosek: <strong>${formatRSD(m.average_ticket)}</strong>
                        </div>
                    </div>
                    <div style="font-family: var(--font-mono); font-weight: 800; color: var(--accent); white-space: nowrap;">${formatRSD(m.total_revenue)}</div>
                `;
                listContainer.appendChild(row);
            });
        } catch (e) {
            console.error("Mechanics greška:", e);
            listContainer.innerHTML = `<div class="error-state-text">${e.message}</div>`;
        }
    }

    function formatRSD(num) {
        return (num || 0).toLocaleString("sr-RS", { maximumFractionDigits: 0 }) + " RSD";
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str).replace(/[&<>"']/g, s => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
        }[s] || s));
    }

    const periodSelect = document.getElementById("mechanics-period");
    if (periodSelect) periodSelect.addEventListener("change", loadMechanicsPerformance);

    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            localStorage.removeItem("token");
            location.reload();
        });
    }

    loadAnalytics();
    loadMechanicsPerformance();
});