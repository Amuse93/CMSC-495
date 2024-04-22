// price_format.js

// JavaScript function to format price to two decimal places
function formatPrice(price) {
    return parseFloat(price).toFixed(2);
}

// Apply formatting to price cells
document.addEventListener("DOMContentLoaded", function() {
    var priceCells = document.querySelectorAll('.product-table tbody td:nth-child(3)');
    priceCells.forEach(function(cell) {
        cell.textContent = formatPrice(cell.textContent);
    });
});