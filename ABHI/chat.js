document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");
    const chatBox = document.getElementById("chat-box");

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    document.getElementById("protectionToggle").addEventListener("change", (e) => {
        const isOn = e.target.checked;
        chrome.storage.local.set({ protectionEnabled: isOn }, () => {
            chatBox.innerHTML += `<div class="ai"><b>ABHI:</b> Protection is now <b>${isOn ? "ON" : "OFF"}</b>.</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        });
    });
});

function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value.trim();
    const chatBox = document.getElementById("chat-box");

    if (!message) return;

    chatBox.innerHTML += `<div class="user"><b>You:</b> ${message}</div>`;
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("https://abhi-shield.onrender.com/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    })
        .then((res) => res.json())
        .then((data) => {
            chatBox.innerHTML += `<div class="ai"><b>ABHI:</b> ${data.reply}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch((err) => {
            console.error("🛑 Fetch error:", err);
            chatBox.innerHTML += `<div class="ai"><b>ABHI:</b> Error reaching brain 😢</div>`;
        });
}

