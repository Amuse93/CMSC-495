function selectRow(row) {
    // Reset styles for all rows
    let rows = document.querySelectorAll('tr');
    rows.forEach(r => r.style.backgroundColor = '');
    
    // Highlight the selected row
    row.style.backgroundColor = 'lightgrey';
    
    // Show the modify button
    let modifyBtn = document.getElementById('modify-btn');
    modifyBtn.style.display = 'block';

    // Get the product ID from the data-product-id attribute of the selected row
    let productID = row.getAttribute('data-product-id');
        
    // Set the href attribute of the modify button with the product ID
    modifyBtn.href = `/modify_product/${productID}`;
    
}