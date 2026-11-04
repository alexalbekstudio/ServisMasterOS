document.addEventListener("DOMContentLoaded", async () => {
    const btnProcess = document.getElementById("btn-process-due");
    const logsList = document.getElementById("logs-list");
    const alertBox = document.getElementById("alert-box");
    const btnLogout = document.getElementById("btn-logout");

    async function loadLogs() {
        try {
            const res = await fetch("/api/v1/reminders/logs", {
                headers: ApiService.getHeaders()
            });
            if (!res.ok) throw new Error("Neuspešno učitavanje logova.");
            const logs = await res.json();

            logsList.innerHTML = "";
            if (!Array.isArray(logs) || logs.length === 0) {
                logsList.innerHTML = `<div class="empty-state-text">Nema poslatih poruka.</div>`;
                return;
            }

            logs.forEach(l => {
                const div = document.createElement("div");
                div.className = "log-item";
                const d = new Date(l.sent_at).toLocaleString("sr-RS");
                div.innerHTML = `
                    <div class="log-header">
                        <span>Do: <strong>${l.recipient_phone}</strong> (${l.channel})</span>
                        <span>${d}</span>
                    </div>
                    <div class="log-msg">${l.message}</div>
                `;
                logsList.appendChild(div);
            });
        } catch (e) {
            logsList.innerHTML = `<div class="error-state-text">${e.message}</div>`;
        }
    }

    btnProcess.addEventListener("click", async () => {
        btnProcess.disabled = true;
        btnProcess.textContent = "Šaljem podsetnike...";
        try {
            const res = await fetch("/api/v1/reminders/process-due", {
                method: "POST",
                headers: ApiService.getHeaders()
            });
            const data = await res.json();
            alertBox.textContent = `Obrada završena! Poslato: ${data.sent_count}, Neuspešno: ${data.failed_count}`;
            alertBox.className = "status-alert success";
            loadLogs();
        } catch (e) {
            alertBox.textContent = e.message;
            alertBox.className = "status-alert error";
        } finally {
            btnProcess.disabled = false;
            btnProcess.textContent = "Pošalji sve dospele podsetnike danas";
        }
    });

    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            ApiService.logout();
        });
    }

    loadLogs();
});