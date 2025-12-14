// =====================================================
// ADMIN UI - Phase 30 Fixed Version
// =====================================================

const sessionGrid = document.getElementById('sessionGrid');
const shiftValue = document.getElementById('shiftValue');
const onlineCount = document.getElementById('onlineCount');
const token = localStorage.getItem('token');
let currentShift = 0;
let onlineUsers = new Set();
let onlineAgents = new Set();
let onlineUsernames = new Set();

const TOTAL_SESSIONS = 8;

// --- HELPERS ---
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// --- GLOBAL STATE ---
window.currentView = null;
window.sessionData = {};
window.socket = null;
window.currentTab = null;

// Initialize Grid (Multi-grid support)
function initGrid() {
    document.querySelectorAll('.monitor-grid').forEach(grid => {
        grid.innerHTML = '';
        for (let i = 1; i <= TOTAL_SESSIONS; i++) {
            const card = document.createElement('div');
            card.className = 'session-card chernobyl-panel p-2 flex flex-col h-[280px] bg-black';

            card.innerHTML = `
                <div class="flex justify-between border-b border-gray-800 mb-2 pb-1">
                    <span class="text-xl font-bold text-green-500 font-mono editable-label" data-key="card_sess_${i}">KANÁL ${i}</span>
                    <span class="text-xs text-gray-600">ID: ${i}</span>
                </div>
                
                <div class="flex justify-between items-center mb-2">
                    <div class="flex items-center gap-2">
                        <span class="bulb status-user-${i}"></span>
                        <span class="text-green-700 font-bold editable-label" data-key="card_user_${i}">OBJEKT ${i}</span>
                    </div>
                </div>

                <div class="flex justify-between items-center bg-gray-900 p-1 rounded border border-gray-800 mb-2">
                    <div class="flex items-center gap-2">
                        <span class="bulb status-agent-${i}"></span>
                        <span class="text-pink-800 font-bold label-agent-${i} editable-label" data-key="card_agent_${i}">STÍN</span>
                    </div>
                    <span class="text-xs text-gray-500" id="sub-agent-dynamic-${i}">ID:${i}</span>
                </div>
                
                <div class="flex-1 overflow-hidden text-xs font-mono p-1 text-gray-300 flex flex-col justify-end chat-box-${i} bg-black border border-green-900/30 inset-shadow">
                </div>
            `;
            grid.appendChild(card);
        }
    });
}

// Update UI based on State
function updateUI() {
    if (shiftValue) shiftValue.innerText = currentShift;
    if (onlineCount) onlineCount.innerText = onlineUsers.size + onlineAgents.size;

    for (let i = 1; i <= TOTAL_SESSIONS; i++) {
        // Update User online status
        const userDots = document.querySelectorAll(`.status-user-${i}`);
        userDots.forEach(dot => {
            if (onlineUsernames.has(`user${i}`)) {
                dot.classList.add('online');
            } else {
                dot.classList.remove('online');
            }
        });

        // Agent in Session i depends on Shift
        let agentIndex = (i - 1 - currentShift) % TOTAL_SESSIONS;
        if (agentIndex < 0) agentIndex += TOTAL_SESSIONS;
        const agentId = agentIndex + 1;
        const agentName = `agent${agentId}`;

        // Update Agent labels
        const agentLabel = document.getElementById(`label-agent-dynamic-${i}`);
        const agentSub = document.getElementById(`sub-agent-dynamic-${i}`);
        if (agentLabel) agentLabel.innerText = agentName.toUpperCase();
        if (agentSub) agentSub.innerText = `ID: ${agentId}`;

        // Update Agent online status
        const agentDots = document.querySelectorAll(`.status-agent-${i}`);
        agentDots.forEach(dot => {
            if (onlineUsernames.has(agentName)) {
                dot.classList.add('online');
            } else {
                dot.classList.remove('online');
            }
        });
    }
}

// === STATION NAVIGATION ===
window.openStation = function(name) {
    console.log("Opening station:", name);
    
    // 1. Hide Hub
    const hubView = document.getElementById('hub-view');
    if (hubView) hubView.classList.add('hidden');

    // 2. Show Nav
    const stationNav = document.getElementById('station-nav');
    if (stationNav) {
        stationNav.classList.remove('hidden');
        stationNav.classList.add('flex');
    }

    // 3. Switch View - hide all first
    document.querySelectorAll('.view-container').forEach(el => el.classList.add('hidden'));
    
    // 4. Show target view
    const view = document.getElementById('view-' + name);
    if (view) {
        view.classList.remove('hidden');
    }

    // 5. Update Title
    const titleMap = {
        'monitor': 'STANICE 1: MONITORING',
        'controls': 'STANICE 2: KONTROLA',
        'economy': 'STANICE 3: EKONOMIKA',
        'tasks': 'STANICE 4: ÚKOLY'
    };
    const titleEl = document.getElementById('station-title');
    if (titleEl) titleEl.innerText = titleMap[name] || name.toUpperCase();

    window.currentView = name;

    // 6. Init specific logic
    if (name === 'economy') refreshEconomy();
    if (name === 'tasks') refreshTasks();
    if (name === 'monitor') {
        if (!window.currentTab) switchMonitorTab('all');
        refreshSystemLogs();
    }
};

window.closeStation = function() {
    // 1. Hide Nav & Views
    const stationNav = document.getElementById('station-nav');
    if (stationNav) {
        stationNav.classList.add('hidden');
        stationNav.classList.remove('flex');
    }
    document.querySelectorAll('.view-container').forEach(el => el.classList.add('hidden'));

    // 2. Show Hub
    const hubView = document.getElementById('hub-view');
    if (hubView) hubView.classList.remove('hidden');
    
    window.currentView = null;
};

window.switchMonitorTab = function(tab) {
    window.currentTab = tab;
    document.querySelectorAll('.mon-tab').forEach(e => e.classList.add('hidden'));
    const tabContent = document.getElementById(`mon-content-${tab}`);
    if (tabContent) tabContent.classList.remove('hidden');

    document.querySelectorAll('#view-monitor .nav-btn').forEach(e => e.classList.remove('active'));
    const btn = document.getElementById(`mtab-${tab}`);
    if (btn) btn.classList.add('active');

    if (tab === 'logs' || tab === 'all') refreshSystemLogs();
    if (tab === 'graph') startGraphLoop();
    else stopGraphLoop();
};

// --- STATE SYNC ---
window.loadControlState = async function() {
    try {
        const res = await fetch('/api/admin/controls/state', { headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) return;
        const data = await res.json();

        // Optimizer
        const optBtn = document.getElementById('btnOptimizer');
        if (optBtn) {
            if (data.optimizer_active) {
                optBtn.innerText = "OPTIMIZER: ON";
                optBtn.classList.remove('bg-gray-800');
                optBtn.classList.add('bg-green-900');
            } else {
                optBtn.innerText = "OPTIMIZER: OFF";
                optBtn.classList.remove('bg-green-900');
                optBtn.classList.add('bg-gray-800');
            }
        }

        // Timer
        const timerInp = document.getElementById('timerInput');
        if (timerInp && document.activeElement !== timerInp) {
            timerInp.value = data.agent_response_window;
        }

        // Power Bar
        const powerBar = document.getElementById('powerBar');
        const powerText = document.getElementById('powerText');
        if (powerBar && powerText) {
            const load = data.power_load || 0;
            const cap = data.power_capacity || 100;
            const pct = Math.min(100, (load / cap) * 100);
            powerBar.style.width = pct + '%';
            powerText.innerText = `${Math.round(load)} / ${cap} MW`;
            powerBar.classList.remove('bg-blue-600', 'bg-red-600');
            powerBar.classList.add(data.is_overloaded ? 'bg-red-600' : 'bg-blue-600');
        }

        // Heat Bar
        const chemBar = document.getElementById('chemBar');
        const chemText = document.getElementById('controlChernobyl');
        if (chemBar && chemText) {
            const temp = data.temperature || 80;
            const maxTemp = 350;
            const pct = Math.min(100, (temp / maxTemp) * 100);
            chemBar.style.width = pct + '%';
            chemText.innerText = `${Math.round(temp)}°`;
        }

        // Shift Display
        const shiftDisplay = document.getElementById('controlShift');
        if (shiftDisplay) shiftDisplay.innerText = data.shift_offset || 0;

        // Power Countdown
        const buyPowerText = document.getElementById('buyPowerText');
        if (buyPowerText && data.power_boost_end_time && data.server_time) {
            const remaining = data.power_boost_end_time - data.server_time;
            if (remaining > 0) {
                const mins = Math.floor(remaining / 60);
                const secs = Math.floor(remaining % 60);
                buyPowerText.innerText = `AKTIVNÍ: ${mins}:${secs.toString().padStart(2, '0')}`;
                if (buyPowerText.parentElement) {
                    buyPowerText.parentElement.classList.add('text-green-400', 'border-green-700');
                }
            } else {
                buyPowerText.innerText = 'PŘIHODIT UHLÍ (+50MW) - 1000 CR';
                if (buyPowerText.parentElement) {
                    buyPowerText.parentElement.classList.remove('text-green-400', 'border-green-700');
                }
            }
        }

    } catch (e) { console.error("Control Sync Fail", e); }
};

// --- NETWORK GRAPH (CANVAS) ---
let graphLoop = null;
function startGraphLoop() {
    if (graphLoop) return;
    const canvas = document.getElementById('networkGraph');
    if (!canvas) return;
    
    const fit = () => {
        canvas.width = canvas.parentElement.offsetWidth;
        canvas.height = canvas.parentElement.offsetHeight;
    };
    window.addEventListener('resize', fit);
    fit();

    const ctx = canvas.getContext('2d');

    const loop = () => {
        ctx.fillStyle = '#111';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        const radius = Math.min(cx, cy) * 0.7;

        ctx.strokeStyle = '#330000';
        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, Math.PI * 2);
        ctx.stroke();

        const time = Date.now() / 1000;

        for (let i = 1; i <= TOTAL_SESSIONS; i++) {
            const angle = (i - 1) / TOTAL_SESSIONS * Math.PI * 2;
            const x = cx + Math.cos(angle) * radius;
            const y = cy + Math.sin(angle) * radius;

            ctx.fillStyle = '#0f0';
            ctx.beginPath();
            ctx.arc(x, y, 8, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#fff';
            ctx.font = '10px monospace';
            ctx.fillText(`U${i}`, x + 10, y + 10);

            let shift = currentShift || 0;
            let agentIndex = (i - 1 - shift) % TOTAL_SESSIONS;
            if (agentIndex < 0) agentIndex += TOTAL_SESSIONS;
            const agentId = agentIndex + 1;

            const innerR = radius * 0.5;
            const agAngle = (agentId - 1) / TOTAL_SESSIONS * Math.PI * 2 + (time * 0.1);
            const agX = cx + Math.cos(agAngle) * innerR;
            const agY = cy + Math.sin(agAngle) * innerR;

            ctx.strokeStyle = `rgba(0, 255, 0, 0.3)`;
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(agX, agY);
            ctx.stroke();

            ctx.fillStyle = '#f0f';
            ctx.beginPath();
            ctx.arc(agX, agY, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#f8f';
            ctx.fillText(`A${agentId}`, agX + 8, agY + 8);
        }

        const pulse = 10 + Math.sin(time * 2) * 5;
        ctx.fillStyle = `rgba(255, 0, 0, ${Math.abs(Math.sin(time))})`;
        ctx.beginPath();
        ctx.arc(cx, cy, pulse, 0, Math.PI * 2);
        ctx.fill();

        graphLoop = requestAnimationFrame(loop);
    };
    graphLoop = requestAnimationFrame(loop);
}

function stopGraphLoop() {
    if (graphLoop) cancelAnimationFrame(graphLoop);
    graphLoop = null;
}

// --- CONTROLS ---
window.triggerShift = function() {
    if (window.socket) {
        window.socket.send(JSON.stringify({ type: 'shift_command' }));
    }
};

window.sendChernobylLevel = function(val) {
    const el = document.getElementById('controlChernobyl');
    if (el) el.innerText = val + "°C";
    if (window.socket) {
        window.socket.send(JSON.stringify({ type: 'temperature_command', value: parseFloat(val) }));
    }
};

window.setMode = function(mode) {
    if (window.socket) {
        window.socket.send(JSON.stringify({ type: 'chernobyl_mode_command', mode: mode }));
    }
};

window.setHyperVis = function(mode) {
    if (window.socket) {
        window.socket.send(JSON.stringify({ type: 'hyper_vis_command', mode: mode }));
    }
};

window.triggerReset = function() {
    if (confirm("RESET SYSTEM?")) {
        if (window.socket) {
            window.socket.send(JSON.stringify({ type: 'reset_game' }));
        }
    }
};

// --- ECONOMY ---
window.refreshEconomy = async function() {
    try {
        const res = await fetch('/api/admin/data/users');
        const users = await res.json();
        const tbody = document.getElementById('economyTableBody');
        if (!tbody) return;
        tbody.innerHTML = '';

        users.forEach(u => {
            const tr = document.createElement('tr');
            let statusClass = "text-green-500";
            if (u.status_level === 'party') statusClass = "text-pink-500 animate-pulse";
            if (u.status_level === 'high') statusClass = "text-yellow-500";

            tr.innerHTML = `
                <td class="p-2 border border-gray-700">${u.id}</td>
                <td class="p-2 border border-gray-700 font-bold text-white">${u.username}</td>
                <td class="p-2 border border-gray-700 ${u.credits < 0 ? 'text-red-500' : 'text-green-500'} font-mono text-right">${u.credits} CR</td>
                <td class="p-2 border border-gray-700 ${statusClass}">${u.status_level.toUpperCase()}</td>
                <td class="p-2 border border-gray-700 ${u.is_locked ? 'text-red-500' : 'text-gray-500'}">${u.is_locked ? 'LOCKED' : 'OPEN'}</td>
                <td class="p-2 border border-gray-700 flex flex-wrap gap-1">
                    <button class="bg-gray-800 text-red-400 border border-gray-600 hover:text-white px-2 py-1 text-xs" onclick="ecoAction('fine', ${u.id})">POKUTA</button>
                    <button class="bg-gray-800 text-green-400 border border-gray-600 hover:text-white px-2 py-1 text-xs" onclick="ecoAction('bonus', ${u.id})">ÚPLATEK</button>
                    <button class="bg-gray-800 text-yellow-400 border border-gray-600 hover:text-white px-2 py-1 text-xs" onclick="ecoAction('toggle_lock', ${u.id})">ZÁMEK</button>
                    <div class="border-l border-gray-600 pl-1 ml-1 flex gap-1">
                        <button class="text-xs px-1 border border-gray-700 text-gray-500 hover:text-white" onclick="setStatus(${u.id}, 'low')">L</button>
                        <button class="text-xs px-1 border border-green-900 text-green-500 hover:text-white" onclick="setStatus(${u.id}, 'mid')">M</button>
                        <button class="text-xs px-1 border border-yellow-900 text-yellow-500 hover:text-white" onclick="setStatus(${u.id}, 'high')">H</button>
                        <button class="text-xs px-1 border border-pink-900 text-pink-500 hover:text-white" onclick="setStatus(${u.id}, 'party')">P</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) { console.error('Eco fetch fail', e); }
};

window.ecoAction = async function(type, userId) {
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
};

window.setStatus = async function(userId, status) {
    try {
        const res = await fetch('/api/admin/economy/set_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, status: status })
        });
        if (res.ok) {
            refreshEconomy();
        } else {
            alert("Status Change Failed");
        }
    } catch (e) { console.error(e); }
};

// --- TASKS ---
window.refreshTasks = async function() {
    if (window.currentView !== 'tasks') return;
    try {
        const res = await fetch('/api/admin/tasks');
        const tasks = await res.json();

        const pendingDiv = document.getElementById('pendingTasksCtx');
        const submitDiv = document.getElementById('submittedTasksCtx');

        if (pendingDiv) pendingDiv.innerHTML = '';
        if (submitDiv) submitDiv.innerHTML = '';

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
                if (pendingDiv) pendingDiv.appendChild(el);
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
                if (submitDiv) submitDiv.appendChild(el);
            }
        });

    } catch (e) { console.error('Task fetch fail', e); }
};

window.approveTask = async function(id) {
    const rewEl = document.getElementById(`rew-${id}`);
    const rew = rewEl ? rewEl.value : 100;
    await fetch('/api/admin/tasks/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: id, reward: parseInt(rew) })
    });
    refreshTasks();
};

window.payTask = async function(id) {
    const ratEl = document.getElementById(`rat-${id}`);
    const rate = ratEl ? ratEl.value : 100;
    await fetch('/api/admin/tasks/pay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: id, rating: parseInt(rate) })
    });
    refreshTasks();
};

// --- WEBSOCKET & MONITOR ---
function initWebSocket() {
    let wsToken = localStorage.getItem('token');
    if (!wsToken) {
        wsToken = getCookie('access_token');
        if (wsToken && wsToken.startsWith('"')) wsToken = wsToken.slice(1, -1);
    }

    console.log("Connecting with token:", wsToken ? "FOUND" : "MISSING");

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/connect`;

    if (typeof SocketClient !== 'undefined') {
        const client = new SocketClient(wsUrl, handleMessage);
        client.connect(wsToken);
        window.socket = {
            send: (data) => client.send(JSON.parse(data))
        };
    } else {
        console.error("SocketClient not loaded");
    }
}

function handleMessage(data) {
    if (data.type === 'init') {
        renderMonitor(data.active_sessions);
    } else if (data.type === 'gamestate_update') {
        if (data.shift !== undefined) {
            currentShift = data.shift;
            const el1 = document.getElementById('monitorShift');
            const el2 = document.getElementById('controlShift');
            if (el1) el1.innerText = data.shift;
            if (el2) el2.innerText = data.shift;
        }
        if (data.temperature !== undefined) {
            updateTemperatureUI(data.temperature);
            const range = document.getElementById('manualChernobyl');
            if (range) range.value = data.temperature;
        }
        if (data.power_load !== undefined) {
            updatePowerUI(data.power_load, data.power_capacity, data.is_overloaded);
        }
        if (data.treasury !== undefined) {
            const el = document.getElementById('treasuryBalance');
            if (el) el.innerText = data.treasury.toLocaleString() + " CR";
        }
        updateUI();
    } else if (data.type === 'status_update') {
        if (data.status === 'online') {
            onlineUsernames.add(data.username);
        } else {
            onlineUsernames.delete(data.username);
        }
        updateUI();
    } else if (data.type === 'message') {
        updateMonitorChat(data);
    }
}

function renderMonitor(sessions) {
    // Handled by initGrid()
}

function updateMonitorChat(msg) {
    const sessId = msg.session_id || 1;
    document.querySelectorAll(`.chat-box-${sessId}`).forEach(chatDiv => {
        const line = document.createElement('div');
        line.innerText = `[${msg.sender}]: ${msg.content}`;
        line.className = "truncate hover:whitespace-normal bg-black mb-1 px-1";
        chatDiv.appendChild(line);
        chatDiv.scrollTop = chatDiv.scrollHeight;
    });
}

// Temperature UI
function updateTemperatureUI(val) {
    const label = document.getElementById('controlChernobyl');
    if (label) label.innerText = Math.round(val) + "°C";

    const bar = document.getElementById('chemBar');
    if (bar) {
        let pct = (val / 350) * 100;
        bar.style.width = Math.min(pct, 100) + "%";

        if (val > 350) {
            bar.style.background = "#ff0000";
        } else if (val > 300) {
            bar.style.background = "linear-gradient(90deg, #ffaa00, #ff4400)";
        } else if (val > 100) {
            bar.style.background = "linear-gradient(90deg, #00ff00, #ffff00)";
        } else {
            bar.style.background = "#00ff00";
        }
    }
}

// Power UI
function updatePowerUI(load, cap, overloaded) {
    const text = document.getElementById('powerText');
    const bar = document.getElementById('powerBar');

    if (text) text.innerText = `${load} / ${cap} MW${overloaded ? " (!)" : ""}`;
    if (bar) {
        const pct = Math.min(100, (load / cap) * 100);
        bar.style.width = pct + "%";

        if (overloaded) {
            bar.classList.remove('bg-blue-600');
            bar.classList.add('bg-red-600', 'animate-pulse');
        } else {
            bar.classList.remove('bg-red-600', 'animate-pulse');
            bar.classList.add('bg-blue-600');
        }
    }
}

// Power Timer
let powerTimerInterval = null;

window.buyPower = async function() {
    if (!confirm("BUY +50MW CAPACITY FOR 1000 CREDITS?")) return;
    try {
        const res = await fetch('/api/admin/power/buy', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            if (data.end_time) {
                startPowerTimer(data.end_time);
            }
        } else {
            alert("TRANSACTION DENIED (Check Funds)");
        }
    } catch (e) { console.error(e); }
};

function startPowerTimer(endTime) {
    const btn = document.getElementById('btnBuyPower');
    const txt = document.getElementById('buyPowerText');
    if (!btn || !txt) return;

    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed');

    if (powerTimerInterval) clearInterval(powerTimerInterval);

    powerTimerInterval = setInterval(() => {
        const now = Date.now() / 1000;
        const diff = endTime - now;

        if (diff <= 0) {
            clearInterval(powerTimerInterval);
            btn.disabled = false;
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
            txt.innerText = "BUY POWER (+50MW) - 1000 CR";
            return;
        }

        const m = Math.floor(diff / 60);
        const s = Math.floor(diff % 60);
        const fmt = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;

        txt.innerText = `[ ACTIVE BOOST: ${fmt} ]`;
    }, 1000);
}

// Edit Mode
let isEditMode = false;
window.toggleEditMode = function() {
    isEditMode = !isEditMode;
    const els = document.querySelectorAll('.editable-label');

    if (isEditMode) {
        els.forEach(el => {
            el.contentEditable = "true";
            el.style.border = "1px dashed #fff";
            el.style.backgroundColor = "rgba(0,0,0,0.5)";
        });
        alert("EDIT MODE ENGAGED. Click text to edit. Toggle off to save.");
    } else {
        const packet = {};
        els.forEach(el => {
            el.contentEditable = "false";
            el.style.border = "none";
            el.style.backgroundColor = "transparent";
            const key = el.dataset.key;
            if (key) packet[key] = el.innerText;
        });

        saveLabelsToServer(packet);
    }
};

async function saveLabelsToServer(labels) {
    try {
        await fetch('/api/admin/labels', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ labels: labels })
        });
    } catch (e) { console.error("Label save failed", e); }
}

async function loadLabels() {
    try {
        const res = await fetch('/api/admin/labels', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            for (const [key, val] of Object.entries(data)) {
                const el = document.querySelector(`.editable-label[data-key="${key}"]`);
                if (el) el.innerText = val;
            }
        }
    } catch (e) { console.warn("No labels loaded"); }
}

// AI Modal
window.toggleAIModal = function() {
    const m = document.getElementById('aiModal');
    if (m) m.classList.toggle('hidden');
};

window.switchConfigTab = function(tab) {
    document.querySelectorAll('.conf-tab').forEach(e => e.classList.add('hidden'));
    const tabEl = document.getElementById(`conf-${tab}`);
    if (tabEl) tabEl.classList.remove('hidden');
};

window.saveKey = async function(provider) {
    const inputEl = document.getElementById(`key-${provider}`);
    if (!inputEl) return;
    const val = inputEl.value;
    await fetch('/api/admin/llm/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: provider, key: val })
    });
    alert('Saved');
};

window.saveConfig = async function(type) {
    alert('Saved (Mock)');
};

// --- SYSTEM LOGS ---
window.refreshSystemLogs = async function() {
    try {
        const res = await fetch('/api/admin/system_logs', { headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) return;
        const logs = await res.json();

        // Mini Log (Overview Tab)
        const mini = document.getElementById('miniLog');
        if (mini) {
            mini.innerHTML = logs.slice(0, 30).map(l => {
                const color = getLogColor(l.event_type);
                return `<div class="mb-1 border-b border-gray-900 pb-1 break-words">
                    <span class="text-gray-600 mr-1">[${new Date(l.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}]</span>
                    <span class="${color}">${l.message}</span>
                </div>`;
            }).join('');
        }

        // Full Log (Logs Tab)
        const full = document.getElementById('fullLog');
        if (full) {
            full.innerHTML = logs.map(l => {
                const color = getLogColor(l.event_type);
                return `<div class="mb-1 font-mono text-sm border-b border-gray-800 pb-1 hover:bg-gray-900/50 break-words">
                    <span class="text-gray-500 mr-2">[${new Date(l.timestamp).toLocaleString()}]</span>
                    <strong class="${color} mr-2">[${l.event_type}]</strong>
                    <span class="text-gray-300">${l.message}</span>
                    ${l.data ? `<span class="text-xs text-gray-600 block ml-8 break-all">${l.data}</span>` : ''}
                </div>`;
            }).join('');
        }
    } catch (e) { console.error("Log fetch failed", e); }
};

window.resetSystemLogs = async function() {
    if (!confirm("CLEAR SYSTEM LOGS? CANNOT BE UNDONE.")) return;
    await fetch('/api/admin/system_logs/reset', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
    refreshSystemLogs();
};

function getLogColor(type) {
    if (type === 'ACTION') return 'text-blue-400';
    if (type === 'ROOT') return 'text-purple-400';
    if (type === 'REPORT') return 'text-orange-400';
    if (type === 'ERROR') return 'text-red-500';
    if (type === 'ALERT') return 'text-yellow-400';
    if (type === 'TASK') return 'text-pink-400';
    return 'text-gray-400';
}

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("Admin UI Loaded");
    initWebSocket();
    initGrid();
    
    // Poll for data
    setInterval(refreshTasks, 5000);
    setInterval(refreshEconomy, 10000);
    setInterval(window.loadControlState, 5000);
    setInterval(refreshSystemLogs, 5000);
    
    window.loadControlState();
    loadLabels();
});
