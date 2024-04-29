document.addEventListener("DOMContentLoaded", function() {
    const addBtn = document.getElementById("add_btn");
    const submitBtn = document.getElementById("submit_btn");
    const acceptBtn = document.getElementById("accept_btn");
    const productTable = document.querySelector(".shelf-product-table tbody");
    const salesTotalSpan = document.getElementById("sales-total");
    const changeReceivedSpan = document.getElementById("change-received");
    const changeDueSpan = document.getElementById("change-due");
    const salesTotalInput = document.getElementById("salesTotalInput");
    const emailInput = document.getElementById("emailInput");


    let orderData = []; // Array to store order data

    addBtn.addEventListener("click", function(event) {
        event.preventDefault();

        const productIdInput = document.getElementById("product_id");
        const quantityInput = document.getElementById("quantity");

        const productId = productIdInput.value.trim();
        const quantity = parseInt(quantityInput.value.trim(), 10);

        if (!productId || isNaN(quantity) || quantity <= 0) {
            alert("Please enter a valid Product ID and Quantity.");
            return;
        }

        const product = products.find(product => product.ProductID === productId);
        if (!product) {
            console.error("Product not found:", productId);
            alert("Product not found.");
            return;
        }

        // Add the entered data to the orderData array
        orderData.push({ ProductID: productId, Product_Name: product.Product_Name, Quantity: quantity, Unit_Price: product.Price });

        // Display the newly added product in the table
        displayProductInTable(productId, product, quantity);

        // Clear input fields
        productIdInput.value = "";
        quantityInput.value = "1";

        updateSummary();
    });

    submitBtn.addEventListener("click", function(event) {
        // Get sales total and email values
        const salesTotal = document.getElementById("sales-total").textContent;
        const email = document.getElementById("email").value;

        // Set values in hidden input fields
        salesTotalInput.value = salesTotal;
        emailInput.value = email;

        // Send the orderData array to the server using AJAX
        submitOrderData(orderData);
    });

    acceptBtn.addEventListener("click", function(event) {
        updateSummary();
    });

    // Function to display a product in the table
    function displayProductInTable(productId, product, quantity) {
        const newRow = document.createElement("tr");
        newRow.innerHTML = `
            <td>${productId}</td>
            <td>${product.Product_Name}</td>
            <td>${quantity}</td>
            <td>${product.Price}</td>
            <td>${product.Price * quantity}</td>
            <td><button class="delete-button">Delete</button></td>
        `;
        productTable.appendChild(newRow);

        // Add event listener for delete button in the newly created row
        const deleteBtn = newRow.querySelector('.delete-button');
        deleteBtn.addEventListener('click', function() {
            deleteProductFromTable(newRow);
        });
    }

    // Function to delete a product from the table
    function deleteProductFromTable(row) {
        const rowIndex = Array.from(productTable.querySelectorAll('tr')).indexOf(row);
        orderData.splice(rowIndex, 1); // Remove the corresponding data from orderData array
        row.remove(); // Remove the row from the table
    }

    // Function to submit order data to the server
    function submitOrderData(data) {

    const salesTotalString = document.getElementById("sales-total").textContent;
    const salesTotal = parseFloat(salesTotalString.replace(/[^\d.-]/g, ''));
    const email = document.getElementById("email").value;

    // Append sales total and email to the order data
    const requestData = {
        orderData: data,
        salesTotal: salesTotal,
        email: email
    };

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/finalize_checkout");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onload = function() {
            if (xhr.status === 200) {
                alert("Order submitted successfully!");
                // Clear the orderData array after sending the data
                orderData = [];
            } else {
                alert("Failed to submit order. Please try again later.");
            }
        };
        xhr.send(JSON.stringify(requestData));
    }

    function updateSummary() {
            let salesTotal = 0;
            orderData.forEach(item => {
                const product = products.find(p => p.ProductID === item.ProductID);
                salesTotal += product.Price * item.Quantity;
            });
            salesTotalSpan.textContent = '$' + salesTotal.toFixed(2);
    
            // Calculate change received and change due (assuming a simple scenario)
            const changeReceived = parseFloat(document.getElementById("received_id").value.trim()) || 0;
            changeReceivedSpan.textContent = '$' + changeReceived.toFixed(2);
            const changeDue = changeReceived - salesTotal;
            changeDueSpan.textContent = '$' + changeDue.toFixed(2);
            document.getElementById("received_id").value = "";
        }

});