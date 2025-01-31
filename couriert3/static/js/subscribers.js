document.querySelector("#subscribe-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    try {
        const response = await fetch(form.action, {
            method: form.method,
            body: formData,
        });

        if (response.ok) {
            const subscribersResponse = await fetch('/api/subscribers');
            const { subscribers } = await subscribersResponse.json();

            const tableBody = document.querySelector("#subscribers-table-body");
            tableBody.innerHTML = ''; // Clear current table
            subscribers.forEach((subscriber) => {
                const row = `<tr>
                    <td>${subscriber.id}</td>
                    <td>${subscriber.email}</td>
                    <td>${subscriber.date_created}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });
            alert("Subscription successful!");
        } else {
            alert("Failed to subscribe. Please try again.");
        }
    } catch (error) {
        alert("An error occurred. Please try again later.");
    }
});
