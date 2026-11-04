/**
 * Auth helper — proverava prijavu.
 * Ako nema tokena, preusmerava na /login.
 */
function requireAuth() {
    if (!localStorage.getItem("token")) {
        window.location.href = "/login";
        return false;
    }
    return true;
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/login";
}

// Poveži sve "Odjava" dugmiće
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("#btn-logout, .header-logout-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            logout();
        });
    });
});