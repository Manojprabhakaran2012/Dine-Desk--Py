/* =====================================================================
   staff.js
   JavaScript specific to the "staff" module.
   Currently: simple live search/filter box for the food items table.
   ===================================================================== */

document.addEventListener("DOMContentLoaded", function () {

    const searchBox = document.getElementById("foodSearch");
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
