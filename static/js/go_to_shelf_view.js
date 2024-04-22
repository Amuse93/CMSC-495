document.addEventListener("DOMContentLoaded", function() {
    // Get the radio button element
    var viewByRadioButton = document.getElementById("viewByShelves");

    // Add event listener for change event
    viewByRadioButton.addEventListener("change", function() {
        // Redirect to the inventory management product view page
        window.location.href = inventoryManagementShelfViewUrl;
    });
});