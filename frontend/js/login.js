document.addEventListener("DOMContentLoaded", () => {
    // Ako je već prijavljen, preusmeri na glavnu
    if (localStorage.getItem("token")) {
        window.location.href = "/";
        return;
    }

    const form = document.getElementById("login-form");
    const btnLogin = document.getElementById("btn-login");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        if (!email || !password) {
            showAlert("Unesite email i lozinku.", "error");
            return;
        }

        btnLogin.disabled = true;
        btnLogin.textContent = "Prijavljujem...";

        try {
            const formData = new URLSearchParams();
            formData.append("username", email);
            formData.append("password", password);

            const res = await fetch("/api/v1/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData,
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || "Pogrešan email ili lozinka.");
            }

            const data = await res.json();
            ApiService.setToken(data.access_token);

            showAlert("Uspešna prijava! Preusmeravam...", "success");
            setTimeout(() => {
                window.location.href = "/";
            }, 500);
        } catch (err) {
            showAlert(err.message, "error");
            btnLogin.disabled = false;
            btnLogin.textContent = "Prijavi se";
        }
    });

    function showAlert(msg, type) {
        const alertBox = document.getElementById("alert-box");
        alertBox.textContent = msg;
        alertBox.className = `status-alert ${type}`;
    }
});