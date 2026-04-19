const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    fetchData();

    document.getElementById('send-btn').addEventListener('click', sendMessage);
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    document.getElementById('refresh-btn').addEventListener('click', () => {
        fetchData();
        addChatMessage("bot", "System data refreshed by admin.");
    });
});

async function fetchData() {
    try {
        const [crowdRes, waitRes, alertsRes] = await Promise.all([
            fetch(`${API_BASE}/crowd`),
            fetch(`${API_BASE}/wait-times`),
            fetch(`${API_BASE}/alerts`)
        ]);

        const crowdData = await crowdRes.json();
        const waitData = await waitRes.json();
        const alertsData = await alertsRes.json();

        updateCrowdUI(crowdData);
        updateWaitUI(waitData);
        updateAlertsUI(alertsData);
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

function updateCrowdUI(data) {
    const container = document.getElementById('crowd-data');
    container.innerHTML = '';

    for (const [location, percentage] of Object.entries(data)) {
        let color = percentage > 80 ? 'red' : percentage > 50 ? 'orange' : 'green';

        container.innerHTML += `
            <div class="data-item">
                <strong>${location}</strong>
                <span style="color: ${color}">${percentage}%</span>
            </div>
        `;
    }
}

function updateWaitUI(data) {
    const container = document.getElementById('wait-data');
    container.innerHTML = '';

    for (const [location, mins] of Object.entries(data)) {
        let color = mins > 20 ? 'red' : mins > 10 ? 'orange' : 'green';

        container.innerHTML += `
            <div class="data-item">
                <strong>${location}</strong>
                <span style="color: ${color}">${mins} min</span>
            </div>
        `;
    }
}

function updateAlertsUI(alerts) {
    const section = document.getElementById('alerts-section');
    const container = document.getElementById('alerts-list');
    container.innerHTML = '';

    if (alerts.length > 0) {
        section.classList.remove('hidden');

        alerts.forEach(alert => {
            const li = document.createElement('li');

            li.style.color =
                alert.severity === "high" ? "red" :
                    alert.severity === "medium" ? "orange" : "green";

            li.textContent = alert.message;
            container.appendChild(li);
        });
    } else {
        section.classList.add('hidden');
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const query = input.value.trim();
    if (!query) return;

    addChatMessage("user", query);
    input.value = '';
    input.focus();

    const thinkingMsg = addChatMessage("bot", "Thinking...");

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        const data = await res.json();
        thinkingMsg.textContent = data.response;

    } catch (error) {
        console.error(error);
        thinkingMsg.textContent = "Server not responding. Please check backend.";
    }
}

function addChatMessage(sender, text) {
    const window = document.getElementById('chat-window');
    const msg = document.createElement('div');

    msg.className = `message ${sender}`;
    msg.textContent = text;

    window.appendChild(msg);
    window.scrollTop = window.scrollHeight;

    return msg;
}