  // Sample data
  const orders = [
    { id: 1, customer: "Amit Patel", item: "Tulip Bulbs", cost: 199.99, status: "Intransit", reason: "" },
    { id: 2, customer: "Suman Reddy", item: "Tulsi Plant", cost: 249.99, status: "Out-for-Delivery", reason: "" },
    { id: 3, customer: "David Lee", item: "Bamboo Plant", cost: 699.99, status: "Failed-Delivery", reason: "Address Not Found" },
    { id: 4, customer: "Mary Johnson", item: "Money Plant", cost: 129.99, status: "Delivered", reason: "" },
    { id: 5, customer: "James Brown", item: "Rose Plant", cost: 59.99, status: "Pending-Delivery", reason: "" },
    { id: 6, customer: "Anjali Rao", item: "Rose Bush", cost: 299.99, status: "Out-for-Delivery", reason: "" },
    { id: 7, customer: "Vikram Singh", item: "Aloe Vera Plant", cost: 179.99, status: "Intransit", reason: "" },
    { id: 8, customer: "Neha Kaur", item: "Orchid Flower", cost: 349.99, status: "Failed-Delivery", reason: "Customer refused Delivery" },
    { id: 9, customer: "Ravi Kumar", item: "Palm Tree", cost: 499.99, status: "Delivered", reason: "" },
    { id: 10, customer: "Sakshi Joshi", item: "Ficus Plant", cost: 279.99, status: "Pending-Delivery", reason: "" }
];

// Function to render report issue orders
function renderReportIssueOrders() {
    const table = document.getElementById('issueTable');
    table.innerHTML = '<tr><th>Order ID</th><th>Customer Name</th><th>Status</th><th>Delivery Issue</th><th>Details</th><th>Action</th></tr>'; // Reset table

    orders.filter(order => 
        order.status !== "Failed-Delivery" && 
        order.status !== "Delivered"
    ).forEach(order => {
        const row = table.insertRow();
        row.insertCell(0).innerText = order.id;
        row.insertCell(1).innerText = order.customer;
        row.insertCell(2).innerHTML = `<span class="status-icon ${order.status.replace(/\s/g, '-')}"">${order.status}</span>`;
        const issueCell = row.insertCell(3);
        issueCell.innerHTML = ` 
            <select data-order-id="${order.id}" onchange="toggleIssueDetail(${order.id})">
                <option value="Wrong Address">Wrong Address</option>
                <option value="Customer not available">Customer not available</option>
                <option value="Customer refused Delivery">Customer refused Delivery</option>
                <option value="Package Damaged">Package Damaged</option>
                <option value="Unable to Locate address">Unable to Locate address</option>
                <option value="Weather Delay">Weather Delay</option>
                <option value="Vehicle Breakdown">Vehicle Breakdown</option>
                <option value="Other">Other</option>
            </select>
        `;
        const detailsCell = row.insertCell(4);
        detailsCell.innerHTML = `<textarea id="issue-detail-${order.id}" placeholder="Enter issue details..." class="hidden"></textarea>`;
        const actionCell = row.insertCell(5);
        const button = document.createElement('button');
        button.innerText = 'Submit';
        button.onclick = function () {
            reportIssue(order.id);  // Ensure this is the correct ID for each order 
        };
        actionCell.appendChild(button);
    });
}

// Function to toggle the reason input for "Other"
function toggleIssueDetail(orderId) {
    const issueSelect = document.querySelector(`#issueTable select[data-order-id="${orderId}"]`);
    const detailTextarea = document.getElementById(`issue-detail-${orderId}`);
    if (issueSelect.value === "Other") {
        detailTextarea.classList.remove("hidden");
    } else {
        detailTextarea.classList.add("hidden");
    }
}

// Function to report an issue
function reportIssue(id) {
    const order = orders.find(order => order.id === id);
    const issueSelect = document.querySelector(`#issueTable select[data-order-id="${id}"]`);
    const issue = issueSelect.value;
    const details = document.querySelector(`#issueTable #issue-detail-${id}`).value;

    // Set status based on issue
    if (["Weather Delay", "Vehicle Breakdown", "Unable to Locate address", "Customer not available"].includes(issue)) {
        order.status = "Pending-Delivery";
    } else {
        order.status = "Failed-Delivery";
    }
    order.reason = issue === "Other" ? details : issue;

    alert(`Order ID ${id} - Issue Reported: ${issue}`);
    renderReportIssueOrders();  // Refresh the issue report
}

// Function to display order details in modal
function showOrderDetails(orderId) {
    const order = orders.find(order => order.id === orderId);
    document.getElementById('modalOrderId').textContent = order.id;
    document.getElementById('modalCustomerName').textContent = order.customer;
    document.getElementById('modalItemName').textContent = order.item;
    document.getElementById('modalCost').textContent = order.cost;
    document.getElementById('modalStatus').textContent = order.status;
    const failedReason = document.getElementById('failedReason');
    failedReason.classList.toggle('hidden', order.status !== 'Failed-Delivery');
    document.getElementById('modalReason').textContent = order.reason;
    document.getElementById('orderModal').style.display = "block";
}

// Function to close modal
function closeModal() {
    document.getElementById('orderModal').style.display = "none";
}

// Initial render of report issue orders
renderReportIssueOrders();
