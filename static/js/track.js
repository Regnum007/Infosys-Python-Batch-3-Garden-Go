document.addEventListener("DOMContentLoaded", () => {
    const status = document.getElementById("status")?.textContent;
    const progressBar = document.getElementById("progress-bar");
    const progressContainer = document.getElementById("progress-container");
    const progressText = document.getElementById("progress-text");

    if (status) {
        progressContainer.style.display = "block";
        let progress = 0;

        switch (status) {
            case "Dispatched":
                progress = 20;
                break;
            case "In Transit":
                progress = 50;
                break;
            case "Out for Delivery":
                progress = 80;
                break;
            case "Delivered":
                progress = 100;
                break;
            case "Failed Attempt":
                progress = 0;
                break;
            default:
                progress = 0;
        }

        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${progress}% Complete`;
    }
});
