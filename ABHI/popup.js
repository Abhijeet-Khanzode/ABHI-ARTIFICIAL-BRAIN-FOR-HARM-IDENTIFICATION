function sendMessage() {
    const input = document.getElementById("userInput");
    const chatBox = document.getElementById("chat-box");
    const message = input.value.trim();
    if (!message) return;

    chatBox.innerHTML += `<div style="color:black; margin: 5px 0;"><b>You:</b> ${message}</div>`;
    input.value = "";

    fetch("https://abhi-shield.onrender.com/ABHI/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
        .then(res => res.json())
        .then(data => {
            // chatBox.innerHTML += `<div><b>ABHI:</b> ${data.reply}</div>`;
            chatBox.innerHTML += `<div style="color: black; margin: 5px 0;"><b>You:</b> ${message}</div>`;
            chatBox.innerHTML += `<div style="color: darkblue; margin: 5px 0;"><b>ABHI:</b> ${data.reply}</div>`;

        })
        .catch(err => {
            chatBox.innerHTML += `<div><b>ABHI:</b> Network error. Try again later.</div>`;
        });
}


// popup.js


document.addEventListener("DOMContentLoaded", () => {
    chrome.runtime.sendMessage({ action: "lastCheckedURL" }, (response) => {
        if (response && response.url) {
            document.getElementById("urlField").value = response.url;
        }
    });

    const form = document.getElementById("feedbackForm");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = {
            name: form.name.value,
            email: form.email.value,
            issue: form.issue.value,
            url: form.url.value
        };

        fetch("https://abhi-shield.onrender.com/feedback-review", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        })
            .then(res => res.json())
            .then(data => {
                document.getElementById("msg").textContent =
                    "Thank you for your contribution..!\nOur team will carefully review this site and respond to your feedback shortly.\nIn the meantime, please stay alert and avoid sharing any personal or sensitive information.\n— With care, \nABHI Team ";
                form.reset();
            })
            .catch(err => {
                document.getElementById("msg").textContent = "❌ Failed to submit. Try again later.";
            });
    });

    const toggle = document.getElementById("toggleProtection");

    // Load current setting
    chrome.storage.local.get("abhi_protection", (data) => {
        toggle.checked = data.abhi_protection ?? true;
    });

    // Update on toggle
    toggle.addEventListener("change", () => {
        chrome.storage.local.set({ abhi_protection: toggle.checked });
    });
});
