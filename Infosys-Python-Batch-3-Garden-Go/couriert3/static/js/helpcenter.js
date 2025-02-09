
        document.addEventListener("DOMContentLoaded", () => {
        // Modal functionality
        const modal = document.getElementById("modal");
        const modalText = document.getElementById("modal-text");
        const closeBtn = document.querySelector(".close-btn");
    
        document.querySelectorAll(".details-btn").forEach(button => {
            button.addEventListener("click", () => {
                modalText.textContent = button.getAttribute("data-content");
                modal.style.display = "flex";
            });
        });
    
        closeBtn.addEventListener("click", () => {
            modal.style.display = "none";
        });
    
        window.addEventListener("click", (event) => {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    
        // Back-to-top button functionality
        const backToTop = document.getElementById("back-to-top");
        window.addEventListener("scroll", () => {
            if (window.scrollY > 300) {
                backToTop.style.display = "block";
            } else {
                backToTop.style.display = "none";
            }
        });
    
        backToTop.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    });
    
    