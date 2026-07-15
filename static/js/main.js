/* =====================================================================
   main.js
   Shared JavaScript used on every page:
   - Sidebar toggle for mobile view
   - Auto-hide flash messages after a few seconds
   ===================================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // ---------------- Sidebar toggle (mobile) ----------------
    const toggleBtn = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("open");
        });
    }

    // ---------------- Auto-hide flash messages ----------------
    const flashMessages = document.querySelectorAll(".flash-message");
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.transition = "opacity 0.5s ease";
            msg.style.opacity = "0";
            setTimeout(function () {
                msg.remove();
            }, 500);
        }, 4000); // messages disappear after 4 seconds
    });

});
