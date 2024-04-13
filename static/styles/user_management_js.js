function selectRow(row) {
    // Reset styles for all rows
    let rows = document.querySelectorAll('tr');
    rows.forEach(r => r.style.backgroundColor = '');
    
    // Highlight the selected row
    row.style.backgroundColor = 'lightgrey';
    
    // Show the modify button
    let modifyBtn = document.getElementById('modify-btn');
    modifyBtn.style.display = 'block';

// Get the employee ID from the data-user-id attribute of the selected row
    let employeeID = row.getAttribute('data-user-id');
    
    // Set the href attribute of the modify button with the employee ID
    modifyBtn.href = '/modify_user/${employeeID}';
}