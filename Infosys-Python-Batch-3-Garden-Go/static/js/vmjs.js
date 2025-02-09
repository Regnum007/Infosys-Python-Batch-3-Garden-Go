
// Filtering Orders
const filterDropdown = document.getElementById('order-filter');
const ordersBody = document.getElementById('orders-body');
const exportBtn = document.getElementById('export-btn');

filterDropdown.addEventListener('change', () => {
    const selectedStatus = filterDropdown.value;
    const rows = ordersBody.querySelectorAll('tr');

    rows.forEach(row => {
        if (selectedStatus === 'all' || row.dataset.status === selectedStatus) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

// Export to Word (DOC) file
exportBtn.addEventListener('click', () => {
    const rows = Array.from(ordersBody.querySelectorAll('tr')).filter(row => row.style.display !== 'none');
    const tableContent = rows.map(row => {
        const cells = row.querySelectorAll('td');
        return Array.from(cells).map(cell => cell.textContent).join('\t');
    }).join('\n');

    const blob = new Blob([tableContent], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'orders.doc';
    link.click();
});


