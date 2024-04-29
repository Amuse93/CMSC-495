document.addEventListener("DOMContentLoaded", function() {
const scopeSelect = document.getElementById("scope");
const productIDDiv = document.getElementById("product_id_input");

// Function to toggle visibility of ProductID input div based on Scope selection
function toggleProductIDInput() {
    if (scopeSelect.value === "Individual_Product") {
        productIDDiv.style.display = "block";  // Show ProductID input div
        document.getElementById("product_id").required = true;  // Make input required
    } else {
        productIDDiv.style.display = "none";  // Hide ProductID input div
        document.getElementById("product_id").value = "";  // Clear input value
        document.getElementById("product_id").required = false;  // Make input optional
    }
}

// Add event listener to Scope dropdown to trigger visibility toggle
scopeSelect.addEventListener("change", toggleProductIDInput);

// Initial call to set initial visibility based on initial Scope value
toggleProductIDInput();
});