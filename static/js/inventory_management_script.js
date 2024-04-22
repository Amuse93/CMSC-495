function selectRow(row) {
    // Reset styles for all rows
    let rows = document.querySelectorAll('tr');
    rows.forEach(r => r.style.backgroundColor = '');
    
    // Highlight the selected row
    row.style.backgroundColor = 'lightgrey';
    
    // Define buttons
    let stockBtn = document.getElementById('stock-btn');
    let moveBtn = document.getElementById('move-product-btn');
    let reportWasteBtn = document.getElementById('report-waste-btn');
    let deleteProductBtn = document.getElementById('delete-product-btn');

    // Show buttons
    stockBtn.style.display = 'block';
    moveBtn.style.display = 'block';
    reportWasteBtn.style.display = 'block';
    deleteProductBtn.style.display = 'block';

    // Get the product ID from the data-product-id attribute of the selected row
    let productID = row.getAttribute('data-product-id');
    let shelfID = row.getAttribute('data-shelf-id');
    
    // Set the href attribute of the buttons with the product ID
    stockBtn.href = `/stock_product/${productID}`;
    moveBtn.href = `/move_product/${productID}&${shelfID}`;
    reportWasteBtn.href = `/report_waste/${productID}&${shelfID}`;
    deleteProductBtn.href = `/delete_product_from_shelf/${productID}&${shelfID}`;
}