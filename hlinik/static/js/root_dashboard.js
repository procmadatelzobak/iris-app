    // Root UI Logic - Simplified/Inline
    // Get token: URL param > sessionStorage
    const urlParams = new URLSearchParams(window.location.search);
    let token = urlParams.get('token') || sessionStorage.getItem('token');

    if (token) {
        sessionStorage.setItem('token', token);
    } else {
        window.location.href = '/';
    }

    // --- STATE ---
    let currentView = 'dashboard';
    let rootState = {};
    let isPanic = false;

    // --- SOCKET ---
    const wsUrl = (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws/connect';
    const client = new SocketClient(wsUrl, handlePayload, (s) => { console.log("WS", s) });
    client.connect(token);

    // Init Constants
    setTimeout(() => fetchRootState(), 1000);

    async function fetchRootState() {
        try {
            const res = await fetch('/api/admin/root/state', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            rootState = data;
            document.getElementById('inTax').value = data.tax_rate;
            document.getElementById('inPower').value = data.power_cap;

            if (data.task_rewards) {
                document.getElementById('rewardDefault').value = data.task_rewards.default;
                document.getElementById('rewardLow').value = data.task_rewards.low;
                document.getElementById('rewardMid').value = data.task_rewards.mid;
                document.getElementById('rewardHigh').value = data.task_rewards.high;
                document.getElementById('rewardParty').value = data.task_rewards.party;
            }
        } catch (e) { console.error(e); }
    }

    function buildConstantsPayload() {
        const rewards = rootState.task_rewards || {};
        const costs = rootState.costs || {};
        return {
            tax_rate: parseFloat(document.getElementById('inTax').value),
            power_cap: parseFloat(document.getElementById('inPower').value),
            temp_threshold: rootState.temp_threshold || 350,
            temp_reset_val: rootState.temp_reset_val || 80,
            temp_min: rootState.temp_min || 20,
            cost_base: costs.base || 10,
            cost_user: costs.user || 5,
            cost_autopilot: costs.autopilot || 10,
            cost_low_latency: costs.low_latency || 30,
            cost_optimizer: costs.optimizer || 15,
            task_reward_default: parseInt(document.getElementById('rewardDefault').value || rewards.default || 0),
            task_reward_low: parseInt(document.getElementById('rewardLow').value || rewards.low || 0),
            task_reward_mid: parseInt(document.getElementById('rewardMid').value || rewards.mid || 0),
            task_reward_high: parseInt(document.getElementById('rewardHigh').value || rewards.high || 0),
            task_reward_party: parseInt(document.getElementById('rewardParty').value || rewards.party || 0),
        };
    }

    window.applySystemConstants = async () => {
        const payload = buildConstantsPayload();
        await fetch('/api/admin/root/update_constants', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        alert("PHYSICS UPDATED");
    };

    window.saveTaskRewards = async () => {
        const payload = buildConstantsPayload();
        await fetch('/api/admin/root/update_constants', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        alert('Odměny pro úkoly aktualizovány');
        rootState.task_rewards = {
            default: payload.task_reward_default,
            low: payload.task_reward_low,
            mid: payload.task_reward_mid,
            high: payload.task_reward_high,
            party: payload.task_reward_party
        };
    };

    function handlePayload(data) {
        logEvent(data.type);

        // Handle translation updates
        if (data.type === 'translation_update' || data.type === 'language_change' || data.type === 'translations_reset') {
            if (window.translationManager) {
                window.translationManager.handleTranslationUpdate(data);
            }
            if (data.type === 'language_change') {
                const select = document.getElementById('languageModeSelect');
                if (select) select.value = data.language_mode;
            }
            return;
        }

        if (data.type === 'gamestate_update') {
            document.getElementById('valShift').innerText = data.shift;
            document.getElementById('bigShift').innerText = data.shift;
            document.getElementById('valChernobyl').innerText = data.chernobyl + "%";
            if (data.panic_global !== undefined) {
                isPanic = data.panic_global;
                updatePanicBtn();
            }
        }
        if (data.type === 'message') {
            // Update Panopticon
            const sessId = data.session_id || 1;
            const chatDiv = document.getElementById(`rootChat-${sessId}`);
            if (chatDiv) {
                const row = document.createElement('div');
                row.className = `text-xs mb-1 ${data.role === 'agent' ? 'text-pink-400' : 'text-green-400'}`;
                row.innerText = `${data.sender}: ${data.content}`;
                chatDiv.appendChild(row);
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }
        }
    }

    function logEvent(type) {
        // Filter out noisy gamestate_update messages
        if (type === 'gamestate_update') return;

        const div = document.createElement('div');
        div.innerText = `${new Date().toLocaleTimeString()} - ${type}`;
        const logStream = document.getElementById('logStream');
        logStream.prepend(div);

        // Keep log size manageable (max 50 entries)
        while (logStream.children.length > 50) {
            logStream.removeChild(logStream.lastChild);
        }
    }

    // --- NAVIGATION ---
    window.switchView = function (view) {
        document.querySelectorAll('.view-container').forEach(e => e.classList.add('hidden'));
        document.getElementById(`view-${view}`).classList.remove('hidden');
        document.querySelectorAll('.nav-btn').forEach(e => e.classList.remove('active'));
        document.getElementById(`nav-${view}`).classList.add('active');
        currentView = view;

        if (view === 'economy') refreshEconomy();
        if (view === 'surveillance') initGrid();
    }

    // --- ACTIONS ---
    window.triggerShift = () => client.send({ type: 'shift_command' });
    window.injectGlobal = async (amt) => {
        if (!confirm(`Inject ${amt} credits to ALL users?`)) return;
        // Need new API for this? Or loop in JS?
        // Loop in JS is slow. Better API.
        // For now, let's just use loop as iterating 8 users is fine.
        // But better implementation: Backend endpoint.
        // Let's assume we have /api/admin/economy/global_bonus
        // I will create that if needed. For now, loop frontend?
        // We can just reuse `ecoAction` inside a loop from the table data.
        const users = await fetchUsers();
        for (const u of users) {
            await fetch('/api/admin/economy/bonus', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ user_id: u.id, amount: amt, reason: "GOD STIMULUS" })
            });
        }
        alert("EXECUTION COMPLETE");
        refreshEconomy();
    };

    window.resetEconomy = async () => {
        // Loop set to 100? or 0?
        alert("Not implemented yet - Requires specific endpoint to be safe.");
    };

    window.broadcastMsg = () => {
        const msg = prompt("GLOBAL MESSAGE:");
        if (msg) client.send({ type: 'admin_broadcast', content: msg });
        // Note: sockets.py needs to handle 'admin_broadcast' or similar. 
        // Existing logic supports 'broadcast_global' via python but not direct socket cmd for admin maybe?
        // I'll check sockets.py later.
    };

    window.triggerReset = () => {
        if (prompt("TYPE 'NUKE' TO CONFIRM") === 'NUKE') {
            client.send({ type: 'reset_game' });
        }
    };

    window.togglePanic = () => {
        const action = isPanic ? "DEACTIVATE PANIC MODE?" : "ACTIVATE EMERGENCY CENSORSHIP?";
        if (confirm(action)) {
            // Optimistic update
            isPanic = !isPanic;
            updatePanicBtn();
            client.send({ type: 'panic_command', enabled: isPanic });
        }
    };

    function updatePanicBtn() {
        const btn = document.getElementById('btnPanic');
        if (!btn) return;
        if (isPanic) {
            btn.style.background = '#f00';
            btn.style.color = '#fff';
            btn.innerText = "🚨 PANIC ACTIVE 🚨";
            btn.classList.remove('animate-pulse');
        } else {
            btn.style.background = 'transparent';
            btn.style.color = '#f00';
            btn.innerText = "⚠️ PANIC MODE ⚠️";
            btn.classList.add('animate-pulse');
        }
    }

    window.restartServer = async () => {
        if (!confirm("RESTART SERVER? All connections will be dropped temporarily.")) return;
        try {
            const res = await fetch('/api/admin/root/restart', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            alert(data.message);
            setTimeout(() => location.reload(), 5000);
        } catch (e) {
            alert("Restart failed: " + e);
        }
    };

    window.factoryReset = async () => {
        if (prompt("THIS WILL DELETE ALL DATA AND RESTART WITH DEFAULTS.\nType 'FACTORY RESET' to confirm:") !== 'FACTORY RESET') return;
        try {
            const res = await fetch('/api/admin/root/factory_reset', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            alert(data.message);
            setTimeout(() => location.reload(), 8000);
        } catch (e) {
            alert("Factory reset failed: " + e);
        }
    };

    window.setShift = () => {
        const target = document.getElementById('targetShift').value;
        if (target === '' || isNaN(parseInt(target))) {
            alert('Enter a valid shift value (0-7)');
            return;
        }
        client.send({ type: 'set_shift_command', value: parseInt(target) });
        document.getElementById('bigShift').innerText = target;
    };

    window.sendChernobylLevel = (val) => {
        client.send({ type: 'chernobyl_command', level: parseInt(val) });
        document.getElementById('valChernobyl').innerText = val + "%";
    }

    // --- TEST MODE TOGGLE ---
    let testModeActive = false;

    window.toggleTestMode = async () => {
        testModeActive = !testModeActive;

        // Send WebSocket command
        client.send({
            type: 'test_mode_toggle',
            enabled: testModeActive
        });

        updateTestModeUI();
    };

    function updateTestModeUI() {
        const btn = document.getElementById('btnTestMode');
        const label = document.getElementById('testModeLabel');
        const status = document.getElementById('testModeStatus');

        if (testModeActive) {
            label.innerText = 'ENABLED';
            btn.classList.add('border-green-500', 'text-green-500');
            btn.classList.remove('border-gray-700');
            status.innerText = '✅ Quick login buttons will appear on login screen';
            status.classList.remove('text-gray-600');
            status.classList.add('text-green-500');
        } else {
            label.innerText = 'DISABLED';
            btn.classList.remove('border-green-500', 'text-green-500');
            btn.classList.add('border-gray-700');
            status.innerText = '❌ Standard password input required';
            status.classList.remove('text-green-500');
            status.classList.add('text-gray-600');
        }
    }

    // --- AI CONFIGURATION ---
    const llmRoles = {
        task: {
            providerId: 'taskProvider',
            modelSelectId: 'taskModelSelect',
            modelInputId: 'taskModelInput',
            promptId: 'taskSystemPrompt'
        },
        optimizer: {
            providerId: 'optimizerProvider',
            modelSelectId: 'optimizerModelSelect',
            modelInputId: 'optimizerModelInput',
            promptId: 'optimizerSystemPrompt',
            instructionId: 'optimizerInstruction'
        },
        hyper: {
            providerId: 'hyperProvider',
            modelSelectId: 'hyperModelSelect',
            modelInputId: 'hyperModelInput',
            promptId: 'hyperSystemPrompt'
        }
    };

    function getAuthHeaders() {
        return { 'Authorization': `Bearer ${token}` };
    }

    window.onProviderChanged = (role) => {
        refreshModels(role);
    }

    window.onModelSelected = (role) => {
        const config = llmRoles[role];
        const select = document.getElementById(config.modelSelectId);
        const input = document.getElementById(config.modelInputId);
        if (select && input) {
            input.value = select.value;
        }
    }

    window.refreshModels = async (role, selectedModel = '') => {
        const config = llmRoles[role];
        if (!config) return;

        const provider = document.getElementById(config.providerId)?.value;
        const select = document.getElementById(config.modelSelectId);
        const input = document.getElementById(config.modelInputId);

        if (!provider || !select) return;
        select.innerHTML = `<option value="">Načítám...</option>`;

        try {
            const res = await fetch(`/api/admin/llm/models/${provider}`, { headers: getAuthHeaders() });
            const models = await res.json();
            select.innerHTML = '';

            if (models.length === 0) {
                const opt = document.createElement('option');
                opt.value = '';
                opt.innerText = 'Žádné modely (zadejte ručně)';
                select.appendChild(opt);
            }

            models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.innerText = m;
                select.appendChild(opt);
            });

            if (selectedModel && models.includes(selectedModel)) {
                select.value = selectedModel;
            }
        } catch (e) {
            console.error('Model fetch failed', e);
            select.innerHTML = '<option value="">Chyba načítání</option>';
        }

        if (input) {
            input.value = selectedModel || select.value || '';
        }
    }

    function applyConfigToUI(role, cfg) {
        const config = llmRoles[role];
        if (!config || !cfg) return;

        const providerSelect = document.getElementById(config.providerId);
        const promptField = document.getElementById(config.promptId);
        const modelInput = document.getElementById(config.modelInputId);

        if (providerSelect && cfg.provider) providerSelect.value = cfg.provider;
        if (promptField && cfg.system_prompt !== undefined) promptField.value = cfg.system_prompt || '';
        if (modelInput && cfg.model_name) modelInput.value = cfg.model_name;

        refreshModels(role, cfg.model_name || '');

        if (config.instructionId && cfg.prompt !== undefined) {
            const instructionField = document.getElementById(config.instructionId);
            if (instructionField) instructionField.value = cfg.prompt || '';
        }
    }

    function gatherRoleConfig(role) {
        const cfg = llmRoles[role];
        const provider = document.getElementById(cfg.providerId)?.value;
        const select = document.getElementById(cfg.modelSelectId);
        const input = document.getElementById(cfg.modelInputId);
        const systemPrompt = document.getElementById(cfg.promptId)?.value || '';
        const modelName = (input?.value || '').trim() || (select?.value || '').trim();

        return { provider, modelName, systemPrompt };
    }

    window.saveLLMConfig = async (role) => {
        const cfg = llmRoles[role];
        if (!cfg) return;
        const { provider, modelName, systemPrompt } = gatherRoleConfig(role);
        if (!provider || !modelName) {
            alert('Vyplňte poskytovatele i model.');
            return;
        }

        const payload = {
            provider,
            model_name: modelName,
            system_prompt: systemPrompt
        };

        if (cfg.instructionId) {
            payload.prompt = document.getElementById(cfg.instructionId)?.value || '';
        }

        try {
            const res = await fetch(`/api/admin/llm/config/${role}`, {
                method: 'POST',
                headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error(await res.text());
            alert('✅ LLM konfigurace uložena');
        } catch (e) {
            console.error(e);
            alert('❌ Uložení se nezdařilo');
        }
    };

    async function loadLLMConfig() {
        try {
            const res = await fetch('/api/admin/llm/config', { headers: getAuthHeaders() });
            const data = await res.json();
            applyConfigToUI('task', data.task);
            applyConfigToUI('hyper', data.hyper);
            applyConfigToUI('optimizer', data.optimizer);
        } catch (e) {
            console.error('Config load failed', e);
        }
    }

    async function loadApiKeys() {
        try {
            const res = await fetch('/api/admin/llm/keys', { headers: getAuthHeaders() });
            const data = await res.json();
            const placeholders = {
                openai: 'sk-...',
                openrouter: 'sk-or-...',
                gemini: 'AIza...'
            };
            [['openai', 'openaiKey'], ['openrouter', 'openrouterKey'], ['gemini', 'geminiKey']]
                .forEach(([provider, inputId]) => {
                    const input = document.getElementById(inputId);
                    if (!input) return;
                    input.value = '';
                    input.placeholder = data?.[provider] || placeholders[provider];
                });
        } catch (e) {
            console.error('Key fetch failed', e);
        }
    }

    window.saveApiKeys = async () => {
        const providers = ['openai', 'openrouter', 'gemini'];
        const updates = [];

        providers.forEach((provider) => {
            const input = document.getElementById(`${provider}Key`);
            if (input && input.value.trim()) {
                updates.push({ provider, key: input.value.trim() });
            }
        });

        if (updates.length === 0) {
            alert('Zadejte alespoň jeden API klíč.');
            return;
        }

        try {
            for (const upd of updates) {
                const res = await fetch('/api/admin/llm/keys', {
                    method: 'POST',
                    headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
                    body: JSON.stringify(upd)
                });
                if (!res.ok) throw new Error(await res.text());
            }
            alert('✅ API klíče uloženy');
            loadApiKeys();
        } catch (e) {
            console.error(e);
            alert('❌ Uložení klíčů selhalo');
        }
    }

    async function hydrateTestMode() {
        try {
            const res = await fetch('/api/admin/root/ai_config', { headers: getAuthHeaders() });
            const data = await res.json();
            if (data.test_mode !== undefined) {
                testModeActive = data.test_mode;
                updateTestModeUI();
            }
            const optimizerField = document.getElementById('optimizerInstruction');
            if (optimizerField && !optimizerField.value && data.optimizer_prompt) {
                optimizerField.value = data.optimizer_prompt;
            }
        } catch (e) {
            console.error('Test mode hydrate failed', e);
        }
    }

    // Call on init
    setTimeout(() => {
        loadLLMConfig();
        loadApiKeys();
        hydrateTestMode();
    }, 1000);

    // --- ECONOMY TABLE ---
    async function fetchUsers() {
        const res = await fetch('/api/admin/data/users', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return await res.json();
    }

    async function refreshEconomy() {
        const users = await fetchUsers();
        const tbody = document.getElementById('rootEcoTable');
        tbody.innerHTML = '';
        users.forEach(u => {
            const tr = document.createElement('tr');
            tr.className = "border-b border-gray-800 hover:bg-gray-900";
            tr.innerHTML = `
                 <td class="p-2 font-bold">${u.username}</td>
                 <td class="p-2 text-yellow-500">${u.credits}</td>
                 <td class="p-2">${u.status_level}</td>
                 <td class="p-2">
                     <button onclick="ecoAction('bonus', ${u.id}, 100)" class="text-green-500 text-xs">[+100]</button>
                     <button onclick="ecoAction('fine', ${u.id}, 100)" class="text-red-500 text-xs">[-100]</button>
                 </td>
             `;
            tbody.appendChild(tr);
        });
    }

    window.ecoAction = async (type, uid, amt) => {
        await fetch(`/api/admin/economy/${type}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ user_id: uid, amount: amt, reason: "ROOT" })
        });
        refreshEconomy();
    }

    // --- GRID ---
    function initGrid() {
        const grid = document.getElementById('rootGrid');
        if (grid.children.length > 0) return; // already init

        for (let i = 1; i <= 8; i++) {
            grid.innerHTML += `
                <div class="border border-gray-800 bg-black flex flex-col h-40">
                    <div class="bg-gray-900 px-2 py-1 text-xs text-gray-500 flex justify-between">
                        <span>SESSION ${i}</span>
                        <span id="label-sess-${i}">Active</span>
                    </div>
                    <div class="flex-1 overflow-y-auto p-1 font-mono text-[10px]" id="rootChat-${i}"></div>
                </div>
            `;
        }
    }

    // --- LANGUAGE SETTINGS ---
    const languageLabels = {
        'cz': 'Čeština',
        'en': 'English',
        'crazy': 'Crazy Čeština 🤪',
        'czech-iris': 'Čeština + IRIS'
    };

    window.setLanguageMode = async (mode) => {
        const status = document.getElementById('languageStatus');
        try {
            const res = await fetch('/api/translations/language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ language_mode: mode })
            });

            if (res.ok) {
                const label = languageLabels[mode] || mode;
                status.innerText = '✅ Jazyk úspěšně změněn na: ' + label;
                status.classList.remove('text-gray-600', 'text-red-500');
                status.classList.add('text-green-500');
            } else {
                const data = await res.json();
                status.innerText = '❌ Chyba: ' + (data.detail || 'Nepodařilo se změnit jazyk');
                status.classList.remove('text-gray-600', 'text-green-500');
                status.classList.add('text-red-500');
            }
        } catch (e) {
            status.innerText = '❌ Chyba připojení';
            status.classList.remove('text-gray-600', 'text-green-500');
            status.classList.add('text-red-500');
        }
    };

    window.resetAllLabels = async () => {
        if (!confirm('Opravdu chcete resetovat všechny vlastní texty? Tuto akci nelze vrátit zpět.')) return;

        const status = document.getElementById('languageStatus');
        try {
            const res = await fetch('/api/translations/reset-labels', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                status.innerText = '✅ Všechny vlastní texty byly resetovány';
                status.classList.remove('text-gray-600', 'text-red-500');
                status.classList.add('text-green-500');
            } else {
                status.innerText = '❌ Nepodařilo se resetovat texty';
                status.classList.remove('text-gray-600', 'text-green-500');
                status.classList.add('text-red-500');
            }
        } catch (e) {
            status.innerText = '❌ Chyba připojení';
        }
    };

    // Load current language setting
    window.loadLanguageSettings = async () => {
        try {
            const res = await fetch('/api/translations/language-options', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                const select = document.getElementById('languageModeSelect');
                if (select && data.current) {
                    select.value = data.current;
                }
            }
        } catch (e) { console.warn("Language settings load failed"); }
    };

    // Call on init
    setTimeout(loadLanguageSettings, 1200);

    // ============================================
    // SIMULATION CONTROLS
    // ============================================

    let simStatusInterval = null;

    window.startSimulation = async (shortTest) => {
        const mode = shortTest ? 'SHORT TEST (5 min)' : 'FULL (1 hodina)';
        if (!confirm(`Spustit simulaci ${mode}?\n\nSimulace bude běžet na pozadí.`)) return;

        try {
            const res = await fetch('/api/admin/simulation/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ short_test: shortTest })
            });

            const data = await res.json();

            if (data.status === 'started') {
                addSimLog('SUCCESS', `Simulace spuštěna: ${mode}`);
                updateSimButtons(true);
                startSimStatusPolling();
            } else {
                addSimLog('ERROR', data.message || 'Nepodařilo se spustit simulaci');
            }

            if (data.data) {
                updateSimStatus(data.data);
            }
        } catch (e) {
            addSimLog('ERROR', `Chyba: ${e.message}`);
        }
    };

    window.stopSimulation = async () => {
        if (!confirm('Zastavit běžící simulaci?')) return;

        try {
            const res = await fetch('/api/admin/simulation/stop', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const data = await res.json();
            addSimLog('INFO', data.message || 'Zastavuji simulaci...');

            if (data.data) {
                updateSimStatus(data.data);
            }
        } catch (e) {
            addSimLog('ERROR', `Chyba: ${e.message}`);
        }
    };

    window.refreshSimStatus = async () => {
        try {
            const res = await fetch('/api/admin/simulation/status', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const data = await res.json();
            updateSimStatus(data);
        } catch (e) {
            console.error('Simulation status error:', e);
        }
    };

    function updateSimStatus(data) {
        // State
        const stateEl = document.getElementById('simState');
        if (stateEl) {
            stateEl.innerText = (data.state || 'idle').toUpperCase();
            stateEl.className = 'text-2xl font-bold';
            if (data.state === 'running') stateEl.classList.add('text-green-500');
            else if (data.state === 'failed') stateEl.classList.add('text-red-500');
            else if (data.state === 'completed') stateEl.classList.add('text-blue-500');
            else stateEl.classList.add('text-gray-500');
        }

        // Progress
        const progress = data.progress_percent || 0;
        document.getElementById('simProgress').innerText = `${progress.toFixed(1)}%`;
        document.getElementById('simProgressBar').style.width = `${progress}%`;

        // Time
        const elapsed = data.elapsed_seconds || 0;
        const remaining = data.remaining_seconds || 0;
        document.getElementById('simElapsed').innerText = formatTime(elapsed);
        document.getElementById('simRemaining').innerText = formatTime(remaining);

        // Stats from summary
        if (data.summary && data.summary.stats) {
            const stats = data.summary.stats;
            document.getElementById('simUsers').innerText = stats.users_active || 0;
            document.getElementById('simAgents').innerText = stats.agents_active || 0;
            document.getElementById('simAdmins').innerText = stats.admins_active || 0;
            document.getElementById('simMessages').innerText = stats.total_messages || 0;
            document.getElementById('simTasks').innerText = stats.total_tasks || 0;
            document.getElementById('simErrors').innerText = stats.total_errors || 0;
        }

        // Update buttons based on state
        const isRunning = data.state === 'running' || data.state === 'stopping';
        updateSimButtons(isRunning);

        // Stop polling if simulation ended
        if (data.state !== 'running' && data.state !== 'stopping' && simStatusInterval) {
            stopSimStatusPolling();
        }
    }

    function updateSimButtons(isRunning) {
        const btnStartFull = document.getElementById('btnStartFull');
        const btnStartShort = document.getElementById('btnStartShort');
        const btnStop = document.getElementById('btnStop');

        if (btnStartFull) btnStartFull.disabled = isRunning;
        if (btnStartShort) btnStartShort.disabled = isRunning;
        if (btnStop) btnStop.disabled = !isRunning;

        // Visual feedback
        if (isRunning) {
            btnStartFull?.classList.add('opacity-50');
            btnStartShort?.classList.add('opacity-50');
            btnStop?.classList.remove('opacity-50');
        } else {
            btnStartFull?.classList.remove('opacity-50');
            btnStartShort?.classList.remove('opacity-50');
            btnStop?.classList.add('opacity-50');
        }
    }

    function startSimStatusPolling() {
        if (simStatusInterval) clearInterval(simStatusInterval);
        // Poll every 5 seconds to reduce server load
        // Note: Consider WebSocket for real-time updates in high-traffic scenarios
        simStatusInterval = setInterval(async () => {
            await refreshSimStatus();
            await fetchSimLogs();
        }, 5000);
    }

    function stopSimStatusPolling() {
        if (simStatusInterval) {
            clearInterval(simStatusInterval);
            simStatusInterval = null;
        }
    }

    async function fetchSimLogs() {
        try {
            const res = await fetch('/api/admin/simulation/logs?limit=50', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();

            if (data.logs && data.logs.length > 0) {
                const logDiv = document.getElementById('simLogStream');
                logDiv.innerHTML = '';

                data.logs.slice(-30).forEach(log => {
                    const time = log.time ? log.time.split('T')[1]?.split('.')[0] : '';
                    const levelColors = {
                        'INFO': 'text-blue-400',
                        'SUCCESS': 'text-green-400',
                        'WARNING': 'text-yellow-400',
                        'ERROR': 'text-red-400',
                        'PHASE': 'text-purple-400',
                        'LLM': 'text-cyan-400',
                        'USER': 'text-white',
                        'AGENT': 'text-pink-400',
                        'ADMIN': 'text-yellow-500'
                    };
                    const color = levelColors[log.level] || 'text-gray-400';

                    const entry = document.createElement('div');
                    entry.className = `mb-1 ${color}`;
                    entry.innerText = `[${time}] [${log.level}] ${log.message}`;
                    logDiv.appendChild(entry);
                });

                logDiv.scrollTop = logDiv.scrollHeight;
            }
        } catch (e) {
            console.error('Fetch logs error:', e);
        }
    }

    function addSimLog(level, message) {
        const logDiv = document.getElementById('simLogStream');
        const time = new Date().toLocaleTimeString();
        const levelColors = {
            'INFO': 'text-blue-400',
            'SUCCESS': 'text-green-400',
            'ERROR': 'text-red-400'
        };
        const color = levelColors[level] || 'text-gray-400';

        const entry = document.createElement('div');
        entry.className = `mb-1 ${color}`;
        entry.innerText = `[${time}] [${level}] ${message}`;
        logDiv.appendChild(entry);
        logDiv.scrollTop = logDiv.scrollHeight;
    }

    async function loadSimHistory() {
        try {
            const res = await fetch('/api/admin/simulation/history', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();

            const historyDiv = document.getElementById('simHistory');
            if (!data.runs || data.runs.length === 0) {
                historyDiv.innerHTML = '<div class="text-gray-600 text-sm">Žádné předchozí simulace</div>';
                return;
            }

            historyDiv.innerHTML = '';
            data.runs.forEach(run => {
                const date = new Date(run.timestamp).toLocaleString('cs-CZ');
                const statusColor = run.status === 'success' ? 'text-green-500' : 'text-red-500';

                const entry = document.createElement('div');
                entry.className = 'flex justify-between items-center p-2 border border-gray-800 bg-black hover:bg-gray-900';
                entry.innerHTML = `
                    <div>
                        <div class="text-sm">${run.scenario_name}</div>
                        <div class="text-xs text-gray-500">${date}</div>
                    </div>
                    <div class="flex items-center gap-4">
                        <span class="text-xs text-gray-400">${run.duration}s</span>
                        <span class="text-sm font-bold ${statusColor}">${run.status?.toUpperCase()}</span>
                    </div>
                `;
                historyDiv.appendChild(entry);
            });
        } catch (e) {
            console.error('Load history error:', e);
        }
    }

    function formatTime(seconds) {
        if (!seconds || seconds <= 0) return '--:--';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Initialize simulation view when switching to it
    const originalSwitchView = window.switchView;
    window.switchView = function (view) {
        originalSwitchView(view);
        if (view === 'simulation') {
            refreshSimStatus();
            loadSimHistory();
        }
    };

