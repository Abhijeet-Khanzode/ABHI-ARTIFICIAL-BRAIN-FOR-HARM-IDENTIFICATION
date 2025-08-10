let lastCheckedURL = "";
let intervalId = null;
let phishingActive = false;
let activeTabId = null;
let alertInterval = null;

// ✅ Start monitoring active tab
function startMonitoring() {
    intervalId = setInterval(() => {
        chrome.storage.local.get(["protectionEnabled"], (res) => {
            if (res.protectionEnabled === false) {
                console.log("🛑 Protection OFF");
                return;
            }

            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                const currentTab = tabs[0];
                if (!currentTab || !currentTab.url) return;

                activeTabId = currentTab.id;

                if (currentTab.url !== lastCheckedURL) {
                    lastCheckedURL = currentTab.url;
                    checkURL(currentTab.url);
                }
            });
        });
    }, 3000);
}

// ✅ Reactivate on tab switch
chrome.tabs.onActivated.addListener(() => {
    if (!intervalId) startMonitoring();
});

// ✅ React when page fully loads
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (tabId === activeTabId && changeInfo.status === "complete") {
        lastCheckedURL = "";
        checkURL(tab.url);
    }
});

// ✅ Stop monitoring when tab is closed
chrome.tabs.onRemoved.addListener((tabId) => {
    if (tabId === activeTabId) {
        clearInterval(intervalId);
        clearInterval(alertInterval);
        phishingActive = false;
        intervalId = null;
        alertInterval = null;
        activeTabId = null;
        console.log("🛑 Tab closed. Monitoring stopped.");
    }
});

// ✅ Check URL using Flask API
function checkURL(url) {
    if (!url || url.startsWith("chrome://")) return;

    chrome.storage.local.get(["protectionEnabled"], (res) => {
        if (res.protectionEnabled === false) return;

        console.log("📡 Sending URL to Flask for check:", url);

        fetch("http://127.0.0.1:5000/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        })
            .then(res => res.json())
            .then(data => {
                const confidence = data.confidence || 0;
                console.log("📬 Response from Flask:", data);

                if (data.isPhishing && confidence >= 70) {
                    if (!phishingActive) {
                        phishingActive = true;
                        startAlertLoop(url);
                    }

                    const notificationId = "abhi-alert-" + Date.now();

                    chrome.notifications.create(notificationId, {
                        type: "basic",
                        iconUrl: "icons/icon128.png",
                        title: "⚠️ ABHI Alert",
                        message: `Phishing detected:\n${url}`,
                        buttons: [{ title: "❌ Not Phishing" }],
                        priority: 2
                    });
                } else {
                    phishingActive = false;
                    clearInterval(alertInterval);
                    console.log("✅ Safe:", url);
                }
            })
            .catch(err => console.error("Fetch Error:", err));
    });
}

// ✅ Loop alerts every 10s
function startAlertLoop(url) {
    clearInterval(alertInterval);

    alertInterval = setInterval(() => {
        if (!phishingActive) {
            clearInterval(alertInterval);
            return;
        }

        const dynamicId = "abhi-alert-" + Date.now();

        chrome.notifications.create(dynamicId, {
            type: "basic",
            iconUrl: "icons/icon128.png",
            title: "⚠️ ABHI Alert",
            message: `Phishing still active:\n${url}`,
            buttons: [{ title: "❌ Not Phishing" }],
            priority: 2
        });

    }, 10000);
}

// ✅ Handle feedback (false positive)
chrome.notifications.onButtonClicked.addListener((notificationId, buttonIndex) => {
    if (notificationId.startsWith("abhi-alert") && buttonIndex === 0) {
        console.log("📬Thank you for your contribution!\n\nOur team will review this site and get back to you.\n\nUntil then, please stay alert and avoid sharing sensitive information.\n\n— ABHI Team 🛡️");


        fetch("http://127.0.0.1:5000/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                url: lastCheckedURL,
                feedback: "false_positive"

            })
        })
            .then(res => res.json())
            .then(data => {
                console.log("✅ Feedback received by server");
                chrome.windows.create({
                    url: chrome.runtime.getURL("popup.html"),
                    type: "popup",
                    width: 360,
                    height: 460
                });
                phishingActive = false;
                clearInterval(alertInterval);
            })
            .catch(err => console.error("❌ Feedback error:", err));
    }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "lastCheckedURL") {
        sendResponse({ url: lastCheckedURL }); // Send the actual tab URL
    }
});

// ✅ Start monitoring on extension load
startMonitoring();
