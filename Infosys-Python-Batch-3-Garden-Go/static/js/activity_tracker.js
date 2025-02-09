let activityDetected = false;

// Detect user activity (mouse move, keypress, etc.)
document.addEventListener('mousemove', () => activityDetected = true);
document.addEventListener('keypress', () => activityDetected = true);

// Send heartbeat to the server every 30 seconds if activity was detected
setInterval(() => {
    if (activityDetected) {
        fetch('/update_activity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => {
            if (response.status === 401) {
                return response.json(); // Parse JSON to extract redirect URL
            }
        })
        .then(data => {
            if (data && data.redirect) {
                window.location.href = data.redirect; // Redirect the user
            }
        });
        activityDetected = false;
    }
}, 10000);
