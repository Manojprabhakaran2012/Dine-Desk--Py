/* =====================================================================
   user.js
   JavaScript specific to the "user" module.
   Currently: live-updates the estimated order total as quantities change.
   ===================================================================== */

document.addEventListener("DOMContentLoaded", function () {

    const qtyInputs = document.querySelectorAll(".qty-input");
    const totalDisplay = document.getElementById("orderTotal");

    function calculateTotal() {
        let total = 0;
        qtyInputs.forEach(function (input) {
            const price = parseFloat(input.dataset.price) || 0;
            const qty = parseInt(input.value) || 0;
            total += price * qty;
        });
        if (totalDisplay) {
            totalDisplay.textContent = total.toFixed(2);
        }
    }

    qtyInputs.forEach(function (input) {
        input.addEventListener("input", calculateTotal);
    });

    // Calculate once on page load (in case of pre-filled values)
    calculateTotal();

});
