/* =====================================================================
   admin.js
   JavaScript specific to the "admin" module.
   Currently: simple live search/filter box for history tables
   (orders, bookings, parking, users, staff).
   ===================================================================== */

document.addEventListener("DOMContentLoaded", function () {

    const searchBox = document.getElementById("adminSearch");
    const table = document.querySelector(".data-table");

    if (searchBox && table) {
        searchBox.addEventListener("keyup", function () {
            const query = searchBox.value.toLowerCase();
            const rows = table.querySelectorAll("tbody tr");

            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? "" : "none";
            });
        });
    }

});
