const sessionGrid = document.getElementById('sessionGrid');
const shiftValue = document.getElementById('shiftValue');
const onlineCount = document.getElementById('onlineCount');
const token = localStorage.getItem('token');
let currentShift = 0;
let onlineUsers = new Set();
let onlineAgents = new Set();

const TOTAL_SESSIONS = 8;

// Initialize Grid
function initGrid() {
    sessionGrid.innerHTML = '';
    for (let i = 1; i <= TOTAL_SESSIONS; i++) {
        const card = document.createElement('div');
        card.className = 'session-card';
        card.id = `session-${i}`;

        // HTML Structure
        card.innerHTML = `
            <div class="flex justify-between border-b border-gray-800 mb-2 pb-1">
                <span class="text-lg font-bold text-gray-400">SESSION ${i}</span>
                <span class="text-xs text-gray-600">ID: ${i}</span>
            </div>
            
            <!-- User Status -->
            <div class="flex justify-between items-center mb-2">
                <div class="flex items-center gap-2">
                    <span class="status-dot" id="status-user-${i}"></span>
                    <span class="text-green-700 font-bold">USER ${i}</span>
                </div>
                <div class="text-xs text-gray-500">SUBJ-${i}</div>
            </div>

            <!-- Agent Status (Dynamic) -->
            <div class="flex justify-between items-center bg-gray-900 p-1 rounded border border-gray-800">
                <div class="flex items-center gap-2">
                    <span class="status-dot" id="status-agent-dynamic-${i}"></span>
                    <span class="text-pink-800 font-bold" id="label-agent-dynamic-${i}">AGENT ?</span>
                </div>
                <div class="text-xs text-gray-600" id="sub-agent-dynamic-${i}">ROUTED</div>
            </div>
        `;
        sessionGrid.appendChild(card);
    }
}

// Update UI based on State
function updateUI() {
    shiftValue.innerText = currentShift;
    onlineCount.innerText = onlineUsers.size + onlineAgents.size;

    for (let i = 1; i <= TOTAL_SESSIONS; i++) {
        // User i is always in Session i
        const userDot = document.getElementById(`status-user-${i}`);
        // DB IDs for userX usually align with X if seeded cleanly, but we rely on seeding script order.
        // Assuming ID X = User X for visualization simplicity.
        // In productio we'd map logical IDs.
        // Let's assume the backend `get_logical_id` ensures user1 -> ID mismatch handles OK but for "online status" raw IDs are sent.
        // Seed order: Root(1), Admin1-4(2-5), Agent1-8(6-13), User1-8(14-21).
        // Wait, seed script order: Root, Admins, Agents, Users.
        // Agent 1 is ID ~6. User 1 is ID ~14.
        // We need a mapping helper or rely on "username" sent in status.
        // Updated backend sends "username" in status_update!

        // Let's use sets of usernames instead of IDs for easier mapping
        if (onlineUsernames.has(`user${i}`)) {
            userDot.classList.add('online');
        } else {
            userDot.classList.remove('online');
        }

        // Agent in Session i depends on Shift
        // Session I = (AgentIndex + Shift) % Total + 1
        // We need to reverse: Which Agent is serving Session I?
        // AgentIndex = (Session I - 1 - Shift) % Total
        // Python % handles negatives. JS % does not safely for negatives.
        let agentIndex = (i - 1 - currentShift) % TOTAL_SESSIONS;
        if (agentIndex < 0) agentIndex += TOTAL_SESSIONS;

        const agentId = agentIndex + 1;
        const agentName = `agent${agentId}`;

        const agentLabel = document.getElementById(`label-agent-dynamic-${i}`);
        const agentSub = document.getElementById(`sub-agent-dynamic-${i}`);
        const agentDot = document.getElementById(`status-agent-dynamic-${i}`);

        agentLabel.innerText = agentName.toUpperCase();
        agentSub.innerText = `ID: ${agentId}`;

        if (onlineUsernames.has(agentName)) {
            agentDot.classList.add('online');
            // agentLabel.classList.add('text-pink-400');
        } else {
            agentDot.classList.remove('online');
            // agentLabel.classList.remove('text-pink-400');
        }
    }
}

let onlineUsernames = new Set();

// WebSocket
const textUrl = (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws/connect';
const client = new SocketClient(textUrl, (data) => {
    console.log("Admin RX:", data);

    if (data.type === 'init') {
        currentShift = data.shift;
        // Parse raw online IDs to usernames? 
        // Backend 'get_online_status' returns IDs.
        // We need usernames.
        // Let's just track status updates for now or ask backend to send usernames in init.
        // Quick fix: Admin won't know initially connected users by username unless backend update.
        // Assuming backend sends usernames in init would be better.
        // For now, let's just render.
        updateUI();
    }

    if (data.type === 'status_update') {
        if (data.status === 'online') {
            onlineUsernames.add(data.username);
        } else {
            onlineUsernames.delete(data.username);
        }
        updateUI();
    }

    if (data.type === 'gamestate_update') {
        currentShift = data.shift;
        if (data.chernobyl !== undefined) {
            updateChernobylUI(data.chernobyl);
            document.getElementById('chernobylRange').value = data.chernobyl;
        }
        updateUI();
    }

}, (status) => {
    console.log("WS", status);
});

client.connect(token);

// Controls
function triggerShift() {
    client.send({ type: 'shift_command' });
}

function triggerReset() {
    if (confirm("RESET ENTIRE SYSTEM?")) {
        client.send({ type: 'reset_game' });
    }
}

function updateChernobylUI(val) {
    const label = document.getElementById('chernobylValue');
    label.innerText = val + "%";

    // Optional: Add visual feedback to admin dashboard too?
    if (val > 80) label.classList.add('blink');
    else label.classList.remove('blink');

    // Apply global effects
    const body = document.body;
    body.className = '';
    if (val > 20 && val <= 50) body.classList.add('instability-low');
    if (val > 50 && val <= 80) body.classList.add('instability-med');
    if (val > 80) body.classList.add('instability-high');
}

function sendChernobylLevel(val) {
    client.send({ type: 'chernobyl_command', level: parseInt(val) });
}

// Init
initGrid();
loadKeys();
loadConfig();

// --- AI CONFIG LOGIC ---

function toggleAIModal() {
    const modal = document.getElementById('aiModal');
    modal.classList.toggle('hidden');
}

function switchTab(tabId) {
    // Hide all
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    // Show target
    document.getElementById(`tab-${tabId}`).classList.remove('hidden');
}

// KEYS
async function loadKeys() {
    try {
        const res = await fetch('/api/admin/llm/keys', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();

        ['openrouter', 'openai', 'gemini'].forEach(provider => {
            const input = document.getElementById(`key-${provider}`);
            const status = document.getElementById(`status-${provider}`);
            if (data[provider]) {
                input.placeholder = "MASKED: " + data[provider];
                status.innerText = "SET";
                status.classList.add('text-green-500');
            } else {
                status.innerText = "MISSING";
                status.classList.remove('text-green-500');
            }
        });
    } catch (e) {
        console.error("Failed to load keys", e);
    }
}

async function saveKey(provider) {
    const input = document.getElementById(`key-${provider}`);
    const key = input.value.trim();
    if (!key) return; // Don't wipe if empty? Or allow wipe? Let's assume user enters key.

    const status = document.getElementById(`status-${provider}`);
    status.innerText = "SAVING...";

    try {
        const res = await fetch('/api/admin/llm/keys', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ provider: provider, key: key })
        });

        if (res.ok) {
            status.innerText = "SAVED";
            status.classList.add('text-green-500');
            input.value = ""; // Clear for security
            loadKeys(); // Refresh mask
        } else {
            status.innerText = "ERROR";
            status.classList.remove('text-green-500');
        }
    } catch (e) {
        console.error(e);
        status.innerText = "FAIL";
    }
}

// CONFIG
async function loadConfig() {
    try {
        const res = await fetch('/api/admin/llm/config', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();

        // Hyper
        const hyper = data.hyper;
        document.getElementById('hyper-provider').value = hyper.provider;
        document.getElementById('hyper-model').value = hyper.model_name;
        document.getElementById('hyper-prompt').value = hyper.system_prompt;

        // Task - TBD
    } catch (e) {
        console.error("Failed to load config", e);
    }
}

async function saveConfig(type) {
    if (type === 'hyper') {
        const config = {
            provider: document.getElementById('hyper-provider').value,
            model_name: document.getElementById('hyper-model').value,
            system_prompt: document.getElementById('hyper-prompt').value
        };

        const res = await fetch(`/api/admin/llm/config/${type}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(config)
        });

        if (res.ok) {
            alert("MATRIX UPDATED");
        } else {
            alert("UPDATE FAILED");
        }
    }
}
