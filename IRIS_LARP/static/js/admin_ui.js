// =====================================================
// ADMIN UI - Phase 30 Fixed Version
// =====================================================

const sessionGrid = document.getElementById('sessionGrid');
const shiftValue = document.getElementById('shiftValue');
const onlineCount = document.getElementById('onlineCount');
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

// Get authentication token (from localStorage or cookie)
function getAuthToken() {
    let token = localStorage.getItem('token');
    if (!token) {
        token = getCookie('access_token');
        if (token && token.startsWith('"')) token = token.slice(1, -1);
    }
    return token;
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
window.openStation = function (name) {
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
    disableEditMode(); // Force exit edit mode on navigation
    if (name === 'economy') refreshEconomy();
    if (name === 'tasks') refreshTasks();
    if (name === 'monitor') {
        if (!window.currentTab) switchMonitorTab('all');
        refreshSystemLogs();
    }
};

window.closeStation = function () {
    disableEditMode(); // Force exit edit mode
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

window.switchMonitorTab = function (tab) {
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
window.loadControlState = async function () {
    try {
        const res = await fetch('/api/admin/controls/state', { headers: { 'Authorization': `Bearer ${getAuthToken()}` } });
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

        const timerDisplay = document.getElementById('timerDisplay');
        if (timerDisplay) {
            timerDisplay.innerText = `${data.agent_response_window || 0} s`;
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
                buyPowerText.innerText = 'NAVÝŠIT KAPACITU (+50MW) - 1000 CR';
                if (buyPowerText.parentElement) {
                    buyPowerText.parentElement.classList.remove('text-green-400', 'border-green-700');
                }
            }
        }

    } catch (e) { console.error("Control Sync Fail", e); }
};

window.updateTimerPreview = function (value) {
    const timerDisplay = document.getElementById('timerDisplay');
    if (timerDisplay) timerDisplay.innerText = `${value} s`;
};

window.saveResponseTimer = async function () {
    const timerInp = document.getElementById('timerInput');
    if (!timerInp) return;
    const seconds = parseInt(timerInp.value, 10);

    try {
        const res = await fetch('/api/admin/timer', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ seconds })
        });

        if (res.ok) {
            updateTimerPreview(seconds);
            showAdminToast('Limit uložen.');
        } else {
            showAdminToast('Nepodařilo se uložit limit.', true);
        }
    } catch (e) {
        console.error('Timer save failed', e);
        showAdminToast('Nepodařilo se uložit limit.', true);
    }
};

// --- NETWORK GRAPH (CANVAS) ---
let graphLoop = null;
let particles = [];
const MAX_PARTICLES = 100; // Limit particle count for performance
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
    particles = []; // Reset particles

    const loop = () => {
        // Fade trail effect instead of clearing
        ctx.fillStyle = 'rgba(17, 17, 17, 0.15)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        const radius = Math.min(cx, cy) * 0.85; // Increased from 0.7 to 0.85

        const time = Date.now() / 1000;

        // Draw multiple orbital rings with varying opacity
        for (let ring = 0; ring < 3; ring++) {
            const ringRadius = radius * (0.4 + ring * 0.2);
            ctx.strokeStyle = `rgba(51, 0, 0, ${0.3 - ring * 0.1})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(cx, cy, ringRadius, 0, Math.PI * 2);
            ctx.stroke();
        }

        // Draw outer boundary ring
        ctx.strokeStyle = '#330000';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, Math.PI * 2);
        ctx.stroke();

        // User and Agent positions with more dynamic behavior
        for (let i = 1; i <= TOTAL_SESSIONS; i++) {
            const angle = (i - 1) / TOTAL_SESSIONS * Math.PI * 2;

            // Users orbit with slight wobble
            const wobble = Math.sin(time * 0.5 + i) * 15;
            const x = cx + Math.cos(angle) * (radius + wobble);
            const y = cy + Math.sin(angle) * (radius + wobble);

            let shift = currentShift || 0;
            let agentIndex = (i - 1 - shift) % TOTAL_SESSIONS;
            if (agentIndex < 0) agentIndex += TOTAL_SESSIONS;
            const agentId = agentIndex + 1;

            // Agents move in complex spiral patterns
            const agentBaseAngle = (agentId - 1) / TOTAL_SESSIONS * Math.PI * 2;
            const spiralOffset = Math.sin(time * 0.3 + agentId * 0.5) * 0.3;
            const innerR = radius * (0.35 + spiralOffset);
            const agAngle = agentBaseAngle + (time * 0.15) + Math.cos(time * 0.2 + agentId) * 0.5;
            const agX = cx + Math.cos(agAngle) * innerR;
            const agY = cy + Math.sin(agAngle) * innerR;

            // Draw connection lines with varying thickness and glow
            const distance = Math.sqrt((x - agX) ** 2 + (y - agY) ** 2);
            const intensity = Math.max(0, 1 - distance / radius);

            // Multiple connection lines for depth
            for (let layer = 0; layer < 2; layer++) {
                ctx.strokeStyle = layer === 0
                    ? `rgba(0, 255, 0, ${intensity * 0.4})`
                    : `rgba(0, 255, 0, ${intensity * 0.15})`;
                ctx.lineWidth = layer === 0 ? 2 : 4;
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(agX, agY);
                ctx.stroke();
            }

            // Spawn particles along connections (with limit for performance)
            if (particles.length < MAX_PARTICLES && Math.random() < 0.08) {
                particles.push({
                    x: x,
                    y: y,
                    vx: (agX - x) * 0.01,
                    vy: (agY - y) * 0.01,
                    life: 1,
                    color: Math.random() > 0.5 ? [0, 255, 0] : [255, 0, 255]
                });
            }

            // Draw user nodes with glow
            const userPulse = 8 + Math.sin(time * 2 + i) * 2;
            ctx.shadowBlur = 15;
            ctx.shadowColor = '#0f0';
            ctx.fillStyle = onlineUsernames.has(`user${i}`) ? '#0f0' : '#050';
            ctx.beginPath();
            ctx.arc(x, y, userPulse, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;

            // User label
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 11px monospace';
            ctx.fillText(`U${i}`, x + 12, y + 12);

            // Draw agent nodes with different glow
            const agentPulse = 6 + Math.cos(time * 3 + agentId) * 1.5;
            ctx.shadowBlur = 12;
            ctx.shadowColor = '#f0f';
            ctx.fillStyle = onlineUsernames.has(`agent${agentId}`) ? '#f0f' : '#505';
            ctx.beginPath();
            ctx.arc(agX, agY, agentPulse, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;

            // Agent label
            ctx.fillStyle = '#f8f';
            ctx.font = 'bold 10px monospace';
            ctx.fillText(`A${agentId}`, agX + 10, agY + 10);
        }

        // Update and draw particles (batched by color for performance)
        const greenParticles = [];
        const magentaParticles = [];

        particles = particles.filter(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.life -= 0.02;

            if (p.life <= 0) return false;

            // Batch particles by color
            if (p.color[0] === 0) greenParticles.push(p);
            else magentaParticles.push(p);

            return true;
        });

        // Draw green particles in one batch
        if (greenParticles.length > 0) {
            ctx.shadowBlur = 5;
            ctx.shadowColor = '#0f0';
            greenParticles.forEach(p => {
                ctx.fillStyle = `rgba(0, 255, 0, ${p.life})`;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // Draw magenta particles in one batch
        if (magentaParticles.length > 0) {
            ctx.shadowBlur = 5;
            ctx.shadowColor = '#f0f';
            magentaParticles.forEach(p => {
                ctx.fillStyle = `rgba(255, 0, 255, ${p.life})`;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
                ctx.fill();
            });
        }
        ctx.shadowBlur = 0;

        // Central core with complex pulsing (optimized with gradient instead of multiple shadow blurs)
        const coreSize = 15 + Math.sin(time * 2) * 5 + Math.cos(time * 3) * 3;
        const coreAlpha = 0.6 + Math.abs(Math.sin(time * 1.5)) * 0.4;

        // Use radial gradient for glow effect (more efficient than multiple shadow blurs)
        const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreSize + 8);
        gradient.addColorStop(0, `rgba(255, 0, 0, ${coreAlpha})`);
        gradient.addColorStop(0.5, `rgba(255, 0, 0, ${coreAlpha * 0.6})`);
        gradient.addColorStop(0.8, `rgba(255, 0, 0, ${coreAlpha * 0.3})`);
        gradient.addColorStop(1, 'rgba(255, 0, 0, 0)');

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(cx, cy, coreSize + 8, 0, Math.PI * 2);
        ctx.fill();

        // Bright center
        ctx.fillStyle = `rgba(255, 100, 0, ${coreAlpha})`;
        ctx.beginPath();
        ctx.arc(cx, cy, coreSize, 0, Math.PI * 2);
        ctx.fill();

        // Add energy waves from center
        const waveCount = 3;
        for (let w = 0; w < waveCount; w++) {
            const wavePhase = (time * 0.5 + w * (Math.PI * 2 / waveCount)) % (Math.PI * 2);
            const waveRadius = (wavePhase / (Math.PI * 2)) * radius * 0.6;
            const waveAlpha = Math.max(0, 1 - wavePhase / (Math.PI * 2));

            ctx.strokeStyle = `rgba(255, 255, 0, ${waveAlpha * 0.3})`;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(cx, cy, waveRadius, 0, Math.PI * 2);
            ctx.stroke();
        }

        graphLoop = requestAnimationFrame(loop);
    };
    graphLoop = requestAnimationFrame(loop);
}

function stopGraphLoop() {
    if (graphLoop) cancelAnimationFrame(graphLoop);
    graphLoop = null;
}

// --- CONTROLS ---
window.triggerShift = function () {
    if (window.socket) {
        window.socket.send(JSON.stringify({ type: 'shift_command' }));
    }
};

window.sendChernobylLevel = function (val) {
    const el = document.getElementById('controlChernobyl');
    if (el) el.innerText = val + "°C";
    if (window.socket) {
        window.socket.send(JSON.stringify({ type: 'temperature_command', value: parseFloat(val) }));
    }
};

window.setMode = function (mode) {
    if (window.socket) {
        window.socket.send(JSON.stringify({ type: 'chernobyl_mode_command', mode: mode }));
    }
};

window.setHyperVis = function (mode) {
    if (window.socket) {
        window.socket.send(JSON.stringify({ type: 'hyper_vis_command', mode: mode }));
    }
};

window.triggerReset = function () {
    if (confirm("RESET SYSTEM?")) {
        if (window.socket) {
            window.socket.send(JSON.stringify({ type: 'reset_game' }));
        }
    }
};

// --- ECONOMY ---
// Helper to safely get nested translation (format: "section.key" or just "key" for top level)
function t(key, defaultVal) {
    if (!window.TRANS) return defaultVal;

    // Try admin_dashboard section first as most keys are there
    if (window.TRANS.admin_dashboard && window.TRANS.admin_dashboard[key]) {
        return window.TRANS.admin_dashboard[key];
    }
    // Try root level
    if (window.TRANS[key]) return window.TRANS[key];

    return defaultVal;
}

window.refreshEconomy = async function () {
    try {
        const res = await fetch('/api/admin/data/users', {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
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
                    <button class="bg-gray-800 text-red-400 border border-gray-600 hover:text-white px-2 py-1 text-xs" onclick="ecoAction('fine', ${u.id})">${t('eco_btn_fine', 'POKUTA')}</button>
                    <button class="bg-gray-800 text-green-400 border border-gray-600 hover:text-white px-2 py-1 text-xs" onclick="ecoAction('bonus', ${u.id})">${t('eco_btn_bribe', 'ÚPLATEK')}</button>
                    <button class="bg-gray-800 text-yellow-400 border border-gray-600 hover:text-white px-2 py-1 text-xs" onclick="ecoAction('toggle_lock', ${u.id})">${t('eco_btn_lock', 'ZÁMEK')}</button>
                    <div class="border-l border-gray-600 pl-1 ml-1 flex gap-1">
                        <button class="text-xs px-1 border border-gray-700 text-gray-500 hover:text-white" onclick="setStatus(${u.id}, 'low')">${t('eco_status_l', 'L')}</button>
                        <button class="text-xs px-1 border border-green-900 text-green-500 hover:text-white" onclick="setStatus(${u.id}, 'mid')">${t('eco_status_m', 'M')}</button>
                        <button class="text-xs px-1 border border-yellow-900 text-yellow-500 hover:text-white" onclick="setStatus(${u.id}, 'high')">${t('eco_status_h', 'H')}</button>
                        <button class="text-xs px-1 border border-pink-900 text-pink-500 hover:text-white" onclick="setStatus(${u.id}, 'party')">${t('eco_status_p', 'P')}</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) { console.error('Eco fetch fail', e); }
};

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
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(payload)
    });

    refreshEconomy();
};

window.setStatus = async function (userId, status) {
    try {
        const res = await fetch('/api/admin/economy/set_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
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
window.refreshTasks = async function () {
    if (window.currentView !== 'tasks') return;
    try {
        const res = await fetch('/api/admin/tasks', {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        if (!res.ok) {
            console.error('Task fetch fail', res.status);
            return;
        }
        const tasks = await res.json();

        const pendingDiv = document.getElementById('pendingTasksCtx');
        const activeDiv = document.getElementById('activeTasksCtx');
        const submitDiv = document.getElementById('submittedTasksCtx');
        const paidDiv = document.getElementById('paidTasksCtx');

        [pendingDiv, activeDiv, submitDiv, paidDiv].forEach(div => {
            if (div) div.innerHTML = '';
        });

        tasks.forEach(t => {
            const el = document.createElement('div');
            el.className = "bg-gray-900 border border-gray-700 p-3 text-sm space-y-2";

            const rewardInfo = t.reward !== undefined && t.reward !== null ? `<span class="text-yellow-400 text-xs">Odměna: ${t.reward} CR</span>` : '';
            const promptInfo = t.prompt ? `<div class="text-gray-300 italic">„${t.prompt}“</div>` : '<div class="text-gray-600 italic">(bez popisu)</div>';

            if (t.status === 'pending_approval') {
                el.innerHTML = `
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="text-blue-400 font-bold">ŽÁDOST #${t.id} (Uživatel ${t.user_id})</div>
                            ${promptInfo}
                        </div>
                        ${rewardInfo}
                    </div>
                    <div class="mt-2 grid grid-cols-2 gap-2">
                        <div>
                            <label class="text-xs text-gray-500">Odměna</label>
                            <input type="number" value="${t.reward || ''}" placeholder="${t.reward || 0}" class="w-full bg-black text-white p-1" id="rew-${t.id}">
                        </div>
                        <div>
                            <label class="text-xs text-gray-500">Zadání pro uživatele</label>
                            <textarea rows="2" class="w-full bg-black text-white p-1" id="prompt-${t.id}">${t.prompt || ''}</textarea>
                        </div>
                    </div>
                    <div class="mt-2 flex gap-2 justify-end">
                        <button class="btn-action text-green-500" onclick="approveTask(${t.id})">SCHVÁLIT</button>
                    </div>
                `;
                if (pendingDiv) pendingDiv.appendChild(el);
            } else if (t.status === 'active') {
                el.innerHTML = `
                    <div class="text-yellow-400 font-bold">AKTIVNÍ #${t.id} (Uživatel ${t.user_id})</div>
                    ${promptInfo}
                    ${rewardInfo}
                    <div class="text-xs text-gray-500">Čeká na odevzdání uživatele.</div>
                `;
                if (activeDiv) activeDiv.appendChild(el);
            } else if (t.status === 'submitted') {
                el.className = "bg-gray-900 border border-green-700 p-3 text-sm space-y-2 cursor-pointer hover:bg-gray-800 transition";
                el.onclick = () => openGradingModal(t);

                el.innerHTML = `
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="text-green-400 font-bold">ODEVZDÁNO #${t.id} (Uživatel ${t.user_id})</div>
                            ${rewardInfo}
                        </div>
                        <span class="text-xs text-green-500 animate-pulse">🔍 KLIKNI PRO HODNOCENÍ</span>
                    </div>
                    ${promptInfo}
                    <div class="text-white border-l-2 border-gray-500 pl-2 my-1 whitespace-pre-wrap line-clamp-3">${(t.submission || '(prázdné)').substring(0, 100)}${t.submission && t.submission.length > 100 ? '...' : ''}</div>
                `;
                if (submitDiv) submitDiv.appendChild(el);
            } else if (t.status === 'paid') {
                el.innerHTML = `
                    <div class="text-gray-300 font-bold">HOTOVO #${t.id} (Uživatel ${t.user_id})</div>
                    ${promptInfo}
                    ${t.submission ? `<div class="text-white border-l-2 border-gray-700 pl-2">${t.submission}</div>` : ''}
                    <div class="text-xs text-gray-400">Hodnocení: ${t.rating || 0}% | Nabídka: ${t.reward || 0} CR</div>
                `;
                if (paidDiv) paidDiv.appendChild(el);
            }
        });

    } catch (e) { console.error('Task fetch fail', e); }
};

window.approveTask = async function (id) {
    const rewEl = document.getElementById(`rew-${id}`);
    const promptEl = document.getElementById(`prompt-${id}`);
    const rew = rewEl ? rewEl.value : null;
    const promptContent = promptEl ? promptEl.value : null;
    await fetch('/api/admin/tasks/approve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({ task_id: id, reward: rew !== null ? parseInt(rew) : null, prompt_content: promptContent })
    });
    refreshTasks();
};

window.payTask = async function (id) {
    const ratEl = document.getElementById(`rat-${id}`);
    const rate = ratEl ? parseInt(ratEl.value) : 100;
    await fetch('/api/admin/tasks/pay', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({ task_id: id, rating: rate })
    });
    refreshTasks();
};

// --- CUSTOM LABELS (v1.4) ---
let editMode = false;

window.toggleEditMode = function () {
    editMode = !editMode;
    const btn = document.querySelector('button[data-key="btn_labels"]');
    if (btn) btn.innerText = editMode ? "💾 ULOŽIT REALITU" : "PŘEPSAT REALITU";

    if (editMode) {
        document.body.classList.add('edit-mode-active');
        enableLabelEditing();
    } else {
        document.body.classList.remove('edit-mode-active');
        saveLabels();
        disableLabelEditing();
    }
};

window.disableEditMode = function () {
    if (!editMode) return;
    editMode = false;
    document.body.classList.remove('edit-mode-active');
    const btn = document.querySelector('button[data-key="btn_labels"]');
    if (btn) btn.innerText = "PŘEPSAT REALITU";
    disableLabelEditing();
}

function enableLabelEditing() {
    document.querySelectorAll('.editable-label').forEach(el => {
        el.contentEditable = "true";
        el.classList.add('editing-highlight');
        // Prevent enter = new line for simple labels
        el.onkeydown = (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                el.blur();
            }
        };
    });
    showAdminToast("EDIT MODE ENABLED: Click text to edit");
}

function disableLabelEditing() {
    document.querySelectorAll('.editable-label').forEach(el => {
        el.contentEditable = "false";
        el.classList.remove('editing-highlight');
        el.onkeydown = null;
    });
}

async function saveLabels() {
    const labels = {};
    document.querySelectorAll('.editable-label').forEach(el => {
        const key = el.dataset.key;
        if (key) {
            labels[key] = el.innerText.trim();
        }
    });

    try {
        await fetch('/api/admin/labels', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({ labels })
        });
        showAdminToast("REALITY REWRITTEN (Labels Saved)");
    } catch (e) {
        console.error("Label save failed", e);
        showAdminToast("REWRITE FAILED", true);
    }
}

// Initial Label Load for Admin
async function loadAdminLabels() {
    try {
        const res = await fetch('/api/admin/labels', {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        if (res.ok) {
            const labels = await res.json();
            for (const [key, value] of Object.entries(labels)) {
                // Update text
                document.querySelectorAll(`.editable-label[data-key="${key}"]`).forEach(el => {
                    el.innerText = value;
                });
            }
        }
    } catch (e) { console.error(e); }
}

// Hook into init
document.addEventListener('DOMContentLoaded', () => {
    // Other inits...
    loadAdminLabels();
});

// Toast Helper
function showAdminToast(msg, isError = false) {
    const t = document.createElement('div');
    t.innerText = msg;
    t.className = `fixed top-20 right-4 p-4 border text-white font-bold z-50 animate-bounce ${isError ? 'bg-red-900 border-red-500' : 'bg-green-900 border-green-500'}`;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

window.setTaskRating = function (taskId, value, btn) {
    const hidden = document.getElementById(`rat-${taskId}`);
    if (hidden) hidden.value = value;
    document.querySelectorAll(`.rating-btn[data-rating-group='${taskId}']`).forEach(el => {
        if (parseInt(el.dataset.value) === value) {
            el.classList.add('border-yellow-400');
            el.classList.remove('border-gray-700');
        } else {
            el.classList.remove('border-yellow-400');
            el.classList.add('border-gray-700');
        }
    });
    if (btn) {
        btn.blur();
    }
};

// --- GRADING MODAL (Phase 32) ---
let currentGradingTask = null;

window.openGradingModal = function (task) {
    currentGradingTask = task;

    document.getElementById('gradeTaskPrompt').textContent = task.prompt || '(Bez zadání)';
    document.getElementById('gradeTaskSubmission').textContent = task.submission || '(Prázdná odpověď)';
    document.getElementById('gradeUsername').textContent = `User ${task.user_id}`;
    document.getElementById('gradeReward').textContent = task.reward || '0';

    document.getElementById('gradingModal').classList.remove('hidden');
};

window.closeGradingModal = function () {
    document.getElementById('gradingModal').classList.add('hidden');
    currentGradingTask = null;
};

window.gradeTask = async function (ratingModifier) {
    if (!currentGradingTask) {
        console.error('No task selected for grading');
        return;
    }

    try {
        const res = await fetch('/api/admin/tasks/grade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({
                task_id: currentGradingTask.id,
                rating_modifier: ratingModifier
            })
        });

        if (res.ok) {
            const result = await res.json();
            showAdminToast(`Úkol ohodnocen: ${result.net_reward || 0} CR (${ratingModifier * 100}%)`);
            closeGradingModal();
            refreshTasks();
        } else {
            const err = await res.json();
            showAdminToast(`Chyba: ${err.detail || 'Nepodařilo se ohodnotit'}`, 'error');
        }
    } catch (e) {
        console.error('Grade task error:', e);
        showAdminToast('Chyba při ohodnocení úkolu', 'error');
    }
};

// Helper for toast notifications
window.showAdminToast = window.showAdminToast || function (message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-4 py-2 rounded shadow-lg z-50 ${type === 'error' ? 'bg-red-600' : 'bg-green-600'} text-white`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
};

// --- WEBSOCKET & MONITOR ---
function initWebSocket() {
    const wsToken = getAuthToken();

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
    // Handle translation updates (all pages)
    if (data.type === 'translation_update' || data.type === 'language_change' || data.type === 'translations_reset') {
        if (window.translationManager) {
            window.translationManager.handleTranslationUpdate(data);
        }
        return;
    }

    if (data.type === 'admin_refresh_tasks') {
        if (window.currentView === 'tasks') {
            refreshTasks();
        }
        return;
    }

    if (data.type === 'init') {
        renderMonitor(data.active_sessions);
    } else if (data.type === 'gamestate_update') {
        if (data.chernobyl_mode !== undefined) {
            updateModeUI(data.chernobyl_mode);
        }
        if (data.hyper_mode !== undefined) {
            setHyperVisUI(data.hyper_mode);
        }
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

window.buyPower = async function () {
    if (!confirm("BUY +50MW CAPACITY FOR 1000 CREDITS?")) return;
    try {
        const res = await fetch('/api/admin/power/buy', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
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

// Handler to prevent click propagation when in edit mode
function editModeClickHandler(e) {
    // Prevent the click from triggering parent onclick handlers and other listeners
    e.stopImmediatePropagation();
    e.preventDefault();
    // Focus the element for editing
    this.focus();
}

window.toggleEditMode = function () {
    if (isEditMode) {
        disableEditMode();
    } else {
        enableEditMode();
    }
};

window.enableEditMode = function () {
    isEditMode = true;
    const els = document.querySelectorAll('.editable-label');

    // Show non-blocking toast instead of alert
    showAdminToast("EDIT MODE ENGAGED. Click text to edit. Click button again to save.");

    els.forEach(el => {
        el.contentEditable = "true";
        el.style.border = "1px dashed #fff";
        el.style.backgroundColor = "rgba(0,0,0,0.5)";
        el.style.cursor = "text";
        // Add click handler to prevent button actions
        el.addEventListener('click', editModeClickHandler, true);
    });
};

window.disableEditMode = function () {
    if (!isEditMode) return;
    isEditMode = false;
    const els = document.querySelectorAll('.editable-label');
    const packet = {};

    els.forEach(el => {
        el.contentEditable = "false";
        el.style.border = "none";
        el.style.backgroundColor = "transparent";
        el.style.cursor = "";
        // Remove click handler
        el.removeEventListener('click', editModeClickHandler, true);
        const key = el.dataset.key;
        if (key) packet[key] = el.innerText;
    });

    saveLabelsToServer(packet);
    showAdminToast("EDIT MODE SAVED.");
};

async function saveLabelsToServer(labels) {
    try {
        await fetch('/api/admin/labels', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ labels: labels })
        });
    } catch (e) { console.error("Label save failed", e); }
}

async function loadLabels() {
    try {
        const res = await fetch('/api/admin/labels', {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
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
// --- SYSTEM LOGS ---
window.refreshSystemLogs = async function () {
    try {
        const res = await fetch('/api/admin/system_logs', { headers: { 'Authorization': `Bearer ${getAuthToken()}` } });
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

window.resetSystemLogs = async function () {
    if (!confirm("CLEAR SYSTEM LOGS? CANNOT BE UNDONE.")) return;
    await fetch('/api/admin/system_logs/reset', { method: 'POST', headers: { 'Authorization': `Bearer ${getAuthToken()}` } });
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

function showAdminToast(msg, isError = false) {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2 border font-mono text-sm shadow-lg ${isError ? 'bg-red-900 border-red-700 text-red-100' : 'bg-green-900 border-green-700 text-green-100'}`;
    toast.innerText = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2500);
}

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("Admin UI Loaded");
    initWebSocket();
    initGrid();

    // Poll for data
    setInterval(refreshTasks, 5000);
    setInterval(refreshEconomy, 10000);
    setInterval(window.loadControlState, 2000); // Faster poll for responsive feel
    setInterval(refreshSystemLogs, 5000);

    window.loadControlState();
    loadLabels();
});

// Placeholder for updateTemperatureUI, updatePowerUI, setHyperVisUI if not defined elsewhere
// Assuming these are defined globally or in other parts of the code.
// If not, they would need to be added here as well.
function updateTemperatureUI(temp) {
    const el = document.getElementById('monitorTemp');
    if (el) el.innerText = temp + "°C";
}

function updatePowerUI(load, capacity, isOverloaded) {
    const el = document.getElementById('monitorPower');
    if (el) {
        el.innerText = `${load}MW / ${capacity}MW`;
        if (isOverloaded) {
            el.classList.add('text-red-500');
        } else {
            el.classList.remove('text-red-500');
        }
    }
}

function setHyperVisUI(active) {
    const el = document.getElementById('hyperVisStatus');
    if (el) {
        el.innerText = active ? "ACTIVE" : "INACTIVE";
        el.classList.toggle('text-green-500', active);
        el.classList.toggle('text-gray-500', !active);
    }
}

function updateModeUI(mode) {
    const el = document.getElementById('chernobylModeStatus');
    if (el) {
        el.innerText = mode ? "ACTIVE" : "INACTIVE";
        el.classList.toggle('text-red-500', mode);
        el.classList.toggle('text-gray-500', !mode);
    }
}

// Update loadControlState to use new fields
// Assuming 'token' is available in this scope, e.g., from getAuthToken()
window.loadControlState = async function () {
    try {
        const token = getAuthToken(); // Ensure token is retrieved
        const res = await fetch('/api/admin/controls/state', { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.ok) {
            const data = await res.json();
            // Standard UI updates
            updateTemperatureUI(data.temperature);
            updatePowerUI(data.power_load, data.power_capacity, data.is_overloaded);

            // Mode Updates
            if (data.chernobyl_mode !== undefined) updateModeUI(data.chernobyl_mode); // Check for undefined to allow false
            if (data.hyper_visibility_mode !== undefined) setHyperVisUI(data.hyper_visibility_mode);

            // Shift
            const el1 = document.getElementById('monitorShift');
            const el2 = document.getElementById('controlShift');
            if (el1) el1.innerText = "SHIFT: " + data.shift_offset;
            if (el2) el2.innerText = data.shift_offset;

            // Timer
            const slider = document.getElementById('timerInput');
            const disp = document.getElementById('timerDisplay');
            if (slider && document.activeElement !== slider) slider.value = data.agent_response_window;
            if (disp) disp.innerText = data.agent_response_window + " s";

        }
    } catch (e) { console.error(e); }
};
