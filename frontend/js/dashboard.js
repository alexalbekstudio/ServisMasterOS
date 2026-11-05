document.addEventListener("DOMContentLoaded", async () => {
    const btnLogout = document.getElementById("btn-logout");

    // =====================================================
    // 1. KPI + STRUKTURA PRIHODA (postojeće)
    // =====================================================
    async function loadAnalytics() {
        try {
            const res = await fetch("/api/v1/analytics/summary", {
                headers: ApiService.getHeaders()
            });
            if (!res.ok) {
                console.error("Analytics API greška:", res.status);
                return;
            }
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
            if (!res.ok) throw new Error("Greška pri učitavanju.");

            const data = await res.json();
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

    // =====================================================
    // 2. GRAFIKONI
    // =====================================================
    async function loadMonthlyRevenueChart() {
        try {
            const res = await fetch("/api/v1/analytics/charts/monthly-revenue?months=12", {
                headers: ApiService.getHeaders()
            });
            if (!res.ok) return;
            const data = await res.json();

            const ctx = document.getElementById("chart-monthly-revenue");
            if (!ctx) return;

            new Chart(ctx, {
                type: "line",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Prihod (RSD)",
                        data: data.values,
                        borderColor: "#d97706",
                        backgroundColor: "rgba(217, 119, 6, 0.1)",
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: "#d97706",
                        pointRadius: 4,
                        pointHoverRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => formatRSD(ctx.parsed.y)
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (val) => (val / 1000).toFixed(0) + "k"
                            }
                        }
                    }
                }
            });
        } catch (e) { console.error("Chart greška:", e); }
    }

    async function loadOrderStatusesChart() {
        try {
            const res = await fetch("/api/v1/analytics/charts/order-statuses", {
                headers: ApiService.getHeaders()
            });
            if (!res.ok) return;
            const data = await res.json();

            const ctx = document.getElementById("chart-order-statuses");
            if (!ctx) return;

            new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [
                            "#3b82f6", // Prijem
                            "#f59e0b", // Dijagnostika
                            "#ef4444", // Čeka delove
                            "#8b5cf6", // U radu
                            "#10b981", // Završeno
                            "#059669", // Preuzeto
                            "#6b7280", // Otkazano
                        ],
                        borderWidth: 2,
                        borderColor: "#ffffff",
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "right",
                            labels: { font: { size: 12 } }
                        }
                    }
                }
            });
        } catch (e) { console.error("Chart greška:", e); }
    }

    async function loadTopPartsChart() {
        try {
            const res = await fetch("/api/v1/analytics/charts/top-parts?limit=5", {
                headers: ApiService.getHeaders()
            });
            if (!res.ok) return;
            const data = await res.json();

            const ctx = document.getElementById("chart-top-parts");
            if (!ctx) return;

            if (data.labels.length === 0) {
                ctx.parentElement.innerHTML = '<div class="empty-state-text">Nema podataka o prodaji delova.</div>';
                return;
            }

            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Količina",
                        data: data.values,
                        backgroundColor: "#d97706",
                        borderRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        },
                        x: {
                            ticks: {
                                callback: function(val) {
                                    const label = this.getLabelForValue(val);
                                    return label.length > 20 ? label.substring(0, 20) + "..." : label;
                                }
                            }
                        }
                    }
                }
            });
        } catch (e) { console.error("Chart greška:", e); }
    }

    async function loadMechanicsChart() {
        try {
            const res = await fetch("/api/v1/analytics/mechanics?period_days=30", {
                headers: ApiService.getHeaders()
            });
            if (!res.ok) return;
            const data = await res.json();

            const ctx = document.getElementById("chart-mechanics");
            if (!ctx) return;

            if (!data.mechanics || data.mechanics.length === 0) {
                ctx.parentElement.innerHTML = '<div class="empty-state-text">Nema podataka o majstorima.</div>';
                return;
            }

            const labels = data.mechanics.map(m => m.mechanic_name);
            const values = data.mechanics.map(m => m.total_revenue);

            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Prihod (RSD)",
                        data: values,
                        backgroundColor: "#10b981",
                        borderRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (val) => (val / 1000).toFixed(0) + "k"
                            }
                        }
                    }
                }
            });
        } catch (e) { console.error("Chart greška:", e); }
    }

    // =====================================================
    // 3. POMOĆNE
    // =====================================================
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
            ApiService.logout();
        });
    }

    // Init
    loadAnalytics();
    loadMechanicsPerformance();
    loadMonthlyRevenueChart();
    loadOrderStatusesChart();
    loadTopPartsChart();
    loadMechanicsChart();
});