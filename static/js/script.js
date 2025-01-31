document.addEventListener("DOMContentLoaded", () => {
    console.log("Enhanced Navbar loaded successfully.");

    const searchBar = document.querySelector('.search-bar input');
    searchBar.addEventListener('focus', () => {
        searchBar.style.borderColor = '#ffcc00';
    });

    searchBar.addEventListener('blur', () => {
        searchBar.style.borderColor = 'white';
    });
});



// footer javascript
document.addEventListener("DOMContentLoaded", () => {
    const newsletterForm = document.querySelector(".newsletter form");
    newsletterForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const emailInput = newsletterForm.querySelector("input[type='email']");
        alert(`Thank you for subscribing with ${emailInput.value}!`);
        emailInput.value = ""; // Clear input field after submission
    });
});



























