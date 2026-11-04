const API_BASE_URL = "http://localhost:8000/api/v1";

// Ako nema tokena i nismo na login/register/status — preusmeri na login
const PUBLIC_PAGES = ["/login", "/register", "/status"];
const currentPath = window.location.pathname;

if (!localStorage.getItem("token") && !PUBLIC_PAGES.includes(currentPath)) {
    window.location.href = "/login";
}

const ApiService = {
    token: localStorage.getItem("token") || null,

    setToken(token) {
        this.token = token;
        localStorage.setItem("token", token);
    },

    getHeaders() {
        const headers = { "Content-Type": "application/json" };
        if (this.token) {
            headers["Authorization"] = `Bearer ${this.token}`;
        }
        return headers;
    },

    logout() {
        localStorage.removeItem("token");
        window.location.href = "/login";
    },

    async login(email, password) {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Greška pri prijavi");
        }

        const data = await response.json();
        this.setToken(data.access_token);
        return data;
    },

    async searchCustomers(term) {
        const response = await fetch(`${API_BASE_URL}/customers/?search=${encodeURIComponent(term)}`, {
            headers: this.getHeaders(),
        });
        if (!response.ok) throw new Error("Neuspešna pretraga klijenata");
        return await response.json();
    },

    async createCustomer(payload) {
        const response = await fetch(`${API_BASE_URL}/customers/`, {
            method: "POST",
            headers: this.getHeaders(),
            body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error("Neuspešno kreiranje klijenta");
        return await response.json();
    },

    async searchVehicles(plate) {
        const response = await fetch(`${API_BASE_URL}/vehicles/?plate=${encodeURIComponent(plate)}`, {
            headers: this.getHeaders(),
        });
        if (!response.ok) throw new Error("Neuspešna pretraga vozila");
        return await response.json();
    },

    async createVehicle(payload) {
        const response = await fetch(`${API_BASE_URL}/vehicles/`, {
            method: "POST",
            headers: this.getHeaders(),
            body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error("Neuspešno kreiranje vozila");
        return await response.json();
    },

    async createWorkOrder(payload) {
        const response = await fetch(`${API_BASE_URL}/work-orders/`, {
            method: "POST",
            headers: this.getHeaders(),
            body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error("Neuspešno kreiranje radnog naloga");
        return await response.json();
    },

    async addWorkOrderPhoto(workOrderId, photoPayload) {
        const response = await fetch(`${API_BASE_URL}/work-orders/${workOrderId}/photos`, {
            method: "POST",
            headers: this.getHeaders(),
            body: JSON.stringify(photoPayload),
        });
        if (!response.ok) throw new Error("Neuspešno dodavanje fotografije");
        return await response.json();
    }
};

// Registracija PWA Service Worker-a
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker
            .register("/sw.js")
            .then((reg) => console.log("SW aktivan:", reg.scope))
            .catch((err) => console.error("SW greška:", err));
    });
}