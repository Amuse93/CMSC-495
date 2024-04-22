document.addEventListener("DOMContentLoaded", function() {
    const addBtn = document.getElementById("add_btn");
    const submitBtn = document.getElementById("submit_btn");
    const productTable = document.querySelector(".shelf-product-table tbody");

    let orderData = []; // Array to store order data

    addBtn.addEventListener("click", function(event) {
        event.preventDefault();

        const productIdInput = document.getElementById("product_id");
        const quantityInput = document.getElementById("quantity");

        const productId = productIdInput.value.trim();
        const quantity = parseInt(quantityInput.value.trim(), 10);

        if (!productId || isNaN(quantity) || quantity <= 0) {
            alert("Please enter valid Product ID and Quantity.");
            return;
        }

        const product = products.find(product => product.ProductID === productId);
        if (!product) {
            console.error("Product not found:", productId);
            alert("Product not found.");
            return;
        }

        // Add the entered data to the orderData array
        orderData.push({ ProductID: productId, Quantity: quantity });

        const newRow = document.createElement("tr");
        newRow.innerHTML = `
            <td>${productId}</td>
            <td>${product.Product_Name}</td>
            <td>${quantity}</td>
        `;
        productTable.appendChild(newRow);

        productIdInput.value = "";
        quantityInput.value = "";
    });

    submitBtn.addEventListener("click", function(event) {
        // Send the orderData array to the server using AJAX
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/submit_received_order");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify(orderData));

        // Clear the orderData array after sending the data
        orderData = [];
    });

});