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
        // ADMIN UI LOGIC (Window Scoped)

        // --- HELPERS ---
        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
            return null;
        }

        // --- GLOBAL STATE ---
        window.currentView = 'monitor';
        window.sessionData = {};

        // --- INITIALIZATION ---
        document.addEventListener('DOMContentLoaded', () => {
            console.log("Admin UI Loaded");
            initWebSocket();
            switchView('monitor');

            // Poll Tasks every 5 seconds
            setInterval(refreshTasks, 5000);
        });

        // --- NAVIGATION ---
        window.switchView = function (viewName, broadcast = true) {
            console.log("Switching to", viewName);
            window.currentView = viewName;

            // Default Buttons
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            const btn = document.getElementById(`nav-${viewName}`);
            if (btn) btn.classList.add('active');

            // Views
            document.querySelectorAll('.view-container').forEach(el => el.classList.add('hidden'));
            const view = document.getElementById(`view-${viewName}`);
            if (view) view.classList.remove('hidden');

            if (viewName === 'economy') refreshEconomy();
            if (viewName === 'tasks') refreshTasks();

            if (broadcast && window.socket) {
                window.socket.send(JSON.stringify({ type: 'admin_view_sync', view: viewName }));
            }
        }

        // --- CONTROLS ---
        window.triggerShift = function () {
            socket.send(JSON.stringify({ type: 'shift_command' }));
        }

        window.sendChernobylLevel = function (val) {
            document.getElementById('controlChernobyl').innerText = val + "%";
            socket.send(JSON.stringify({ type: 'chernobyl_command', level: parseInt(val) }));
        }

        window.setMode = function (mode) {
            if (window.socket) {
                window.socket.send(JSON.stringify({ type: 'chernobyl_mode_command', mode: mode }));
            }
        }

        window.setHyperVis = function (mode) {
            if (window.socket) {
                window.socket.send(JSON.stringify({ type: 'hyper_vis_command', mode: mode }));
            }
        }

        window.triggerReset = function () {
            if (confirm("RESET SYSTEM?")) {
                socket.send(JSON.stringify({ type: 'reset_game' }));
            }
        }

        // --- ECONOMY ---
        window.refreshEconomy = async function () {
            try {
                const res = await fetch('/api/admin/data/users');
                const users = await res.json();
                const tbody = document.getElementById('economyTableBody');
                tbody.innerHTML = '';

                users.forEach(u => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                <td>${u.id}</td>
                <td class="font-bold text-white">${u.username}</td>
                <td class="${u.credits < 0 ? 'text-red-500' : 'text-green-500'}">${u.credits}</td>
                <td>${u.status_level.toUpperCase()}</td>
                <td class="${u.is_locked ? 'text-red-500' : 'text-gray-500'}">${u.is_locked ? 'LOCKED' : 'OPEN'}</td>
                <td class="flex gap-2">
                    <button class="btn-action text-red-500" onclick="ecoAction('fine', ${u.id})">FINE</button>
                    <button class="btn-action text-green-500" onclick="ecoAction('bonus', ${u.id})">BONUS</button>
                    <button class="btn-action text-yellow-500" onclick="ecoAction('toggle_lock', ${u.id})">LOCK/UNLOCK</button>
                </td>
            `;
                    tbody.appendChild(tr);
                });
            } catch (e) { console.error('Eco fetch fail', e); }
        }

        window.ecoAction = async function (type, userId) {
            let payload = { user_id: userId };

            if (type === 'fine' || type === 'bonus') {
                const amt = prompt("Amount?");
                if (!amt) return;
                payload.amount = parseInt(amt);
                payload.reason = prompt("Reason?") || "Admin Action";
            }

            await fetch(`/api/admin/economy/${type}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            refreshEconomy();
        }

        // --- TASKS ---
        window.refreshTasks = async function () {
            if (window.currentView !== 'tasks') return;
            try {
                const res = await fetch('/api/admin/tasks');
                const tasks = await res.json();

                const pendingDiv = document.getElementById('pendingTasksCtx');
                const submitDiv = document.getElementById('submittedTasksCtx');

                pendingDiv.innerHTML = '';
                submitDiv.innerHTML = '';

                tasks.forEach(t => {
                    const el = document.createElement('div');
                    el.className = "bg-gray-900 border border-gray-700 p-2 text-sm";

                    if (t.status === 'pending_approval') {
                        el.innerHTML = `
                    <div class="text-blue-400 font-bold">TASK #${t.id} (User ${t.user_id})</div>
                    <div class="text-gray-300 italic">"${t.prompt}"</div>
                    <div class="mt-2 flex gap-2">
                        <input type="number" placeholder="Reward" class="w-20 bg-black text-white p-1" id="rew-${t.id}">
                        <button class="btn-action text-green-500" onclick="approveTask(${t.id})">APPROVE</button>
                    </div>
                `;
                        pendingDiv.appendChild(el);
                    } else if (t.status === 'submitted') {
                        el.innerHTML = `
                    <div class="text-green-400 font-bold">SUBMISSION #${t.id} (User ${t.user_id})</div>
                    <div class="text-gray-400 text-xs">OFFER: ${t.reward} CR</div>
                    <div class="text-white border-l-2 border-gray-500 pl-2 my-1">${t.submission}</div>
                    <div class="mt-2 flex gap-2">
                         <input type="range" min="0" max="200" value="100" class="w-24" id="rat-${t.id}">
                         <button class="btn-action text-yellow-500" onclick="payTask(${t.id})">PAY</button>
                    </div>
                `;
                        submitDiv.appendChild(el);
                    }
                });

            } catch (e) { console.error('Task fetch fail', e); }
        }

        window.approveTask = async function (id) {
            const rew = document.getElementById(`rew-${id}`).value || 100;
            await fetch('/api/admin/tasks/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: id, reward: parseInt(rew) })
            });
            refreshTasks();
        }

        window.payTask = async function (id) {
            const rate = document.getElementById(`rat-${id}`).value;
            await fetch('/api/admin/tasks/pay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: id, rating: parseInt(rate) })
            });
            refreshTasks();
        }

        // --- WEBSOCKET & MONITOR ---
        window.socket = null; // Expose socket

        function initWebSocket() {
            let token = localStorage.getItem('token');
            if (!token) {
                // Try cookie
                token = getCookie('access_token');
                // Clean cookie (remove "Bearer " if present? No, jwt is raw)
                // Cookie value usually is just the token string if set by FastAPI
                if (token && token.startsWith('"')) token = token.slice(1, -1); // Remove quotes if any
            }

            console.log("Connecting with token:", token ? "FOUND" : "MISSING");

            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/connect`;

            // Use SocketClient
            if (typeof SocketClient !== 'undefined') {
                const client = new SocketClient(wsUrl, handleMessage);
                client.connect(token);
                window.socket = client.ws; // Store raw WS reference for sends if needed, or use client.send
                // Override global socket.send to use client.send for compatibility
                window.socket = {
                    send: (data) => client.send(JSON.parse(data)) // Wrapper
                };
            } else {
                console.error("SocketClient not loaded");
            }
        }

        function handleMessage(data) {
            if (data.type === 'init') {
                renderMonitor(data.active_sessions); // active_sessions? Init payload has online count.
            } else if (data.type === 'admin_view_sync') {
                // Sync View
                if (data.view !== window.currentView) {
                    switchView(data.view, false); // Do not broadcast back
                }
            } else if (data.type === 'gamestate_update') {
                if (data.shift !== undefined) {
                    const el1 = document.getElementById('monitorShift');
                    const el2 = document.getElementById('controlShift');
                    if (el1) el1.innerText = data.shift;
                    if (el2) el2.innerText = data.shift;
                }
                if (data.chernobyl !== undefined) {
                    const el = document.getElementById('controlChernobyl');
                    if (el) el.innerText = Math.round(data.chernobyl) + "%";
                    const ch_man = document.getElementById('manualChernobyl');
                    if (ch_man) ch_man.value = data.chernobyl;
                }
            } else if (data.type === 'message') {
                updateMonitorChat(data);
            }
        }

        function renderMonitor(sessions) {
            const grid = document.getElementById('sessionGrid');
            if (!grid) return;
            grid.innerHTML = '';

            for (let i = 1; i <= 8; i++) {
                const div = document.createElement('div');
                div.className = 'session-card';
                div.id = `sess-${i}`;
                div.innerHTML = `
             <div class="flex justify-between items-center border-b border-gray-800 pb-1 mb-1">
                 <span class="text-xs text-gray-500">SESSION ${i}</span>
                 <div class="status-dot"></div>
             </div>
             <div class="flex-1 overflow-hidden text-xs font-mono p-1 text-gray-300 flex flex-col justify-end" id="chat-${i}">
                 <!-- logs -->
             </div>
        `;
                grid.appendChild(div);
            }
        }

        function updateMonitorChat(msg) {
            const sessId = msg.session_id || 1;
            const chatDiv = document.getElementById(`chat-${sessId}`);
            if (chatDiv) {
                const line = document.createElement('div');
                line.innerText = `[${msg.sender}]: ${msg.content}`;
                line.className = "truncate hover:whitespace-normal bg-black mb-1";
                chatDiv.appendChild(line);
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }
        }

        // AI Modal Toggles
        window.toggleAIModal = function () {
            const m = document.getElementById('aiModal');
            if (m) m.classList.toggle('hidden');
        }

        window.switchConfigTab = function (tab) {
            document.querySelectorAll('.conf-tab').forEach(e => e.classList.add('hidden'));
            document.getElementById(`conf-${tab}`).classList.remove('hidden');
        }

        window.saveKey = async function (provider) {
            const val = document.getElementById(`key-${provider}`).value;
            await fetch('/api/admin/llm/keys', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider: provider, key: val })
            });
            alert('Saved');
        }

        window.saveConfig = async function (type) {
            alert('Saved (Mock)');
        }
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
            const range = document.getElementById('manualChernobyl');
            if (range) range.value = data.chernobyl;
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
    // 1. Update Text
    const label = document.getElementById('controlChernobyl');
    if (label) label.innerText = Math.round(val) + "%";

    // 2. Update Bar Width
    const bar = document.getElementById('chemBar');
    if (bar) {
        // Infinite effect logic:
        // If > 100, we can wrap mod 100, or clamp?
        // Let's clamp visual width to 100% but change color?
        // Or just let it go to 100% and stay there (while effects go wild).
        // Let's try width = val + "%". If >100, it fills container.
        bar.style.width = Math.min(val, 100) + "%";

        // Color Shift based on level
        if (val > 100) {
            bar.style.background = "linear-gradient(90deg, #ff00ff, #ffffff)"; // Plasma
        } else if (val > 80) {
            bar.style.background = "linear-gradient(90deg, #ff0000, #ffaa00)"; // Critical
        } else {
            bar.style.background = "linear-gradient(90deg, #00ff00, #ffff00, #ff0000)"; // Normal
        }
    }

    // 3. Global Effects (Body)
    const body = document.body;
    body.className = 'bg-gray-900 text-white font-mono'; // Base classes
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
