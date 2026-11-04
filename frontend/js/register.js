document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("token")) {
        window.location.href = "/";
        return;
    }

    const form = document.getElementById("register-form");
    const btnRegister = document.getElementById("btn-register");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const shopName = document.getElementById("shop_name").value.trim();
        const shopPhone = document.getElementById("shop_phone").value.trim();
        const shopCity = document.getElementById("shop_city").value.trim();
        const ownerName = document.getElementById("owner_name").value.trim();
        const ownerEmail = document.getElementById("owner_email").value.trim();
        const ownerPassword = document.getElementById("owner_password").value;

        if (!shopName || !shopPhone || !shopCity || !ownerName || !ownerEmail || !ownerPassword) {
            showAlert("Popunite sva polja.", "error");
            return;
        }

        if (ownerPassword.length < 6) {
            showAlert("Lozinka mora imati najmanje 6 znakova.", "error");
            return;
        }

        btnRegister.disabled = true;
        btnRegister.textContent = "Registrujem...";

        try {
            const res = await fetch("/api/v1/auth/register-shop", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    shop_name: shopName,
                    shop_phone: shopPhone,
                    shop_city: shopCity,
                    owner_name: ownerName,
                    owner_email: ownerEmail,
                    owner_password: ownerPassword,
                }),
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || "Greška pri registraciji.");
            }

            // Auto-login nakon registracije
            const loginFormData = new URLSearchParams();
            loginFormData.append("username", ownerEmail);
            loginFormData.append("password", ownerPassword);

            const loginRes = await fetch("/api/v1/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: loginFormData,
            });

            if (loginRes.ok) {
                const loginData = await loginRes.json();
                ApiService.setToken(loginData.access_token);
            }

            showAlert("Servis je registrovan! Preusmeravam...", "success");
            setTimeout(() => {
                window.location.href = "/";
            }, 800);
        } catch (err) {
            showAlert(err.message, "error");
            btnRegister.disabled = false;
            btnRegister.textContent = "Registruj servis";
        }
    });

    function showAlert(msg, type) {
        const alertBox = document.getElementById("alert-box");
        alertBox.textContent = msg;
        alertBox.className = `status-alert ${type}`;
    }
});