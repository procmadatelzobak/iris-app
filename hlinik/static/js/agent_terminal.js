/**
 * Agent Terminal — logika klientské strany pro operátora
 * Vyžaduje: socket_client.js, sound_engine.js
 * Vyžaduje globální: IRIS_CONFIG.username
 */

(function () {
    var config = window.IRIS_CONFIG || {};
    var currentUsername = config.username || '';

    // Token
    var urlParams = new URLSearchParams(window.location.search);
    var token = urlParams.get('token') || sessionStorage.getItem('token');
    if (token) { sessionStorage.setItem('token', token); }
    else { window.location.href = '/'; return; }

    // DOM
    var sessionIdDisplay = document.getElementById('sessionIdDisplay');
    var chatHistory = document.getElementById('chatHistory');
    var timerLimitDisplay = document.getElementById('timerLimitDisplay');
    var responseWindowDisplay = document.getElementById('responseWindowDisplay');
    var tabId = Math.random().toString(36).substring(7);

    // Překlady
    function t(key, fallback) {
        var manager = window.translationManager;
        if (manager && manager.initialized) {
            var value = manager.get(key);
            if (value && value !== key) return value;
        }
        return fallback;
    }

    function setTimerText(key, fallback) {
        var el = document.getElementById('timerText');
        if (el) el.innerText = t(key, fallback);
    }

    function applyLocalizedText() {
        var input = document.getElementById('msgInput');
        if (input) input.placeholder = t('agent_terminal.message_placeholder', 'Vložte odpověď...');
        var unlock = document.getElementById('unlockPass');
        if (unlock) unlock.placeholder = t('agent_terminal.override_placeholder', 'Zadejte ovládací kód');
        setTimerText('agent_terminal.timer_waiting', 'ČEKÁM NA UŽIVATELE');
    }

    // Timer
    var timerLimit = 120;
    var timerRemaining = 120;
    var timerInterval = null;

    function updateTimerLimitUI(newLimit) {
        if (typeof newLimit === 'number') {
            timerLimit = newLimit;
            timerRemaining = Math.min(timerRemaining, timerLimit);
        }
        if (timerLimitDisplay) timerLimitDisplay.innerText = timerLimit + 's';
        if (responseWindowDisplay) responseWindowDisplay.innerText = timerLimit + 's';
        updateTimerUI();
    }

    applyLocalizedText();
    var translationReady = setInterval(function() {
        if (window.translationManager && window.translationManager.initialized) {
            applyLocalizedText();
            clearInterval(translationReady);
        }
    }, 200);
    updateTimerLimitUI(timerLimit);

    function startTimer() {
        clearInterval(timerInterval);
        timerRemaining = timerLimit;
        updateTimerUI();
        setTimerText('agent_terminal.timer_active', 'ODPOČET AKTIVNÍ');
        document.getElementById('lockOverlay').classList.add('hidden');
        document.getElementById('msgInput').disabled = false;
        timerInterval = setInterval(function() {
            timerRemaining--;
            updateTimerUI();
            if (timerRemaining <= 0) { clearInterval(timerInterval); lockInput(); }
        }, 1000);
    }

    function stopTimer() {
        clearInterval(timerInterval);
        timerRemaining = timerLimit;
        updateTimerUI();
        setTimerText('agent_terminal.timer_stopped', 'ZASTAVENO');
    }

    function lockInput() {
        document.getElementById('lockOverlay').classList.remove('hidden');
        document.getElementById('msgInput').disabled = true;
        setTimerText('agent_terminal.timer_blocked', 'BLOKOVÁNO');
    }

    function updateTimerUI() {
        var bar = document.getElementById('timerBar');
        var pct = (timerRemaining / timerLimit) * 100;
        bar.style.width = pct + '%';
        bar.className = pct < 20
            ? 'h-full bg-red-600 w-full transition-all duration-1000 linear animate-pulse'
            : 'h-full bg-yellow-500 w-full transition-all duration-1000 linear';
    }

    // === WEBSOCKET ===
    var currentSessionId = null;
    var wsUrl = (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws/connect';
    var client = new SocketClient(wsUrl, handleMessage, function(status) { console.log("WS Status", status); });
    client.connect(token);

    function handleMessage(data) {
        if (data.type === 'translation_update' || data.type === 'language_change' || data.type === 'translations_reset') {
            if (window.translationManager) window.translationManager.handleTranslationUpdate(data);
            applyLocalizedText();
            return;
        }

        switch (data.type) {
            case 'gamestate_update':
                if (data.shift !== undefined) document.getElementById('shiftDisplay').innerText = data.shift;
                if (data.temperature !== undefined) {
                    var td = document.getElementById('tempDisplay');
                    if (td) td.innerText = data.temperature;
                }
                if (data.session_id) {
                    currentSessionId = data.session_id;
                    sessionIdDisplay.innerText = "S" + data.session_id;
                }
                if (data.hyper_mode) applyHyperVisibility(data.hyper_mode);
                if (data.agent_window !== undefined) updateTimerLimitUI(data.agent_window);
                break;
            case 'optimizing_start': showOptimizingLoader(); break;
            case 'optimizer_preview': handleOptimizerPreview(data); break;
            case 'typing_sync':
                if (data.tabId !== tabId) {
                    var inp = document.getElementById('msgInput');
                    if (inp.value !== data.content) inp.value = data.content;
                }
                break;
            case 'system_alert': showSystemAlert(data.content); break;
            case 'session_timeout':
                lockInput();
                setTimerText('agent_terminal.timer_timeout', 'ČAS VYPRŠEL');
                if (window.sfx) sfx.playError();
                break;
            case 'error':
                showSystemAlert(data.msg || 'Chyba');
                if (window.sfx) sfx.playError();
                break;
            case 'typing_start': showTypingIndicator(true); break;
            case 'typing_stop': showTypingIndicator(false); break;
            default:
                showTypingIndicator(false);
                if (data.session_id) sessionIdDisplay.innerText = "S" + data.session_id;
                appendMessage(data);
                if (data.sender !== currentUsername) {
                    if (window.sfx) sfx.playReceive();
                    if (data.role === 'user') startTimer();
                } else {
                    stopTimer();
                }
                break;
        }
    }

    // === INPUT ===
    document.getElementById('msgInput').addEventListener('input', function(e) {
        client.send({ type: 'typing_sync', content: e.target.value, tabId: tabId });
    });

    document.getElementById('chatForm').addEventListener('submit', function(e) {
        e.preventDefault();
        var input = document.getElementById('msgInput');
        var text = input.value.trim();
        if (text) {
            client.send({ content: text });
            client.send({ type: 'typing_sync', content: "", tabId: tabId });
            appendMessage({ sender: currentUsername, role: 'agent', content: text });
            input.value = '';
            if (window.sfx) sfx.playSend();
            stopTimer();
        }
    });

    document.getElementById('msgInput').addEventListener('keydown', function() {
        if (window.sfx) sfx.playType();
    });

    // === AUTOPILOT ===
    var isAutopilotOn = false;
    window.toggleAuto = function() {
        isAutopilotOn = !isAutopilotOn;
        client.send({ type: 'autopilot_toggle', status: isAutopilotOn });
        var autoBtn = document.querySelector('button[onclick="toggleAuto()"]');
        if (isAutopilotOn) {
            if (autoBtn) { autoBtn.innerText = "[ AUTOPILOT: AKTIVNÍ ]"; autoBtn.classList.add('bg-pink-600'); }
            if (window.sfx) sfx.playTone(600, 'square', 0.1, 0.1);
        } else {
            if (autoBtn) { autoBtn.innerText = "[ TOGGLE AUTOPILOT ]"; autoBtn.classList.remove('bg-pink-600'); }
            if (window.sfx) sfx.playTone(300, 'sawtooth', 0.1, 0.1);
        }
    };

    // === OPTIMIZER ===
    function showOptimizingLoader() {
        var input = document.getElementById('msgInput');
        input.disabled = true;
        input.placeholder = ">> PROBÍHÁ OPTIMALIZACE <<";
        var div = document.createElement('div');
        div.id = 'optimizingLoader';
        div.className = 'chat-bubble agent opacity-50 animate-pulse text-[10px] border border-pink-500 bg-pink-900/50';
        div.textContent = 'PROBÍHÁ OPTIMALIZACE ODPOVĚDI...';
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function handleOptimizerPreview(data) {
        var loader = document.getElementById('optimizingLoader');
        if (loader) loader.remove();

        var div = document.createElement('div');
        div.id = 'optimizerConfirmBox';
        div.className = 'border border-pink-500 bg-black p-2 text-xs mb-2';

        var header = document.createElement('div');
        header.className = 'text-pink-300 font-bold mb-1 text-[10px]';
        header.textContent = 'OPTIMALIZACE DOKONČENA';
        div.appendChild(header);

        var orig = document.createElement('div');
        orig.className = 'mb-1 text-gray-500 line-through text-[9px]';
        orig.textContent = data.original;
        div.appendChild(orig);

        var rewritten = document.createElement('div');
        rewritten.className = 'mb-2 text-green-400 font-bold text-sm';
        rewritten.textContent = data.rewritten;
        div.appendChild(rewritten);

        var btns = document.createElement('div');
        btns.className = 'flex gap-1';

        var confirmBtn = document.createElement('button');
        confirmBtn.className = 'flex-1 bg-green-700 hover:bg-green-600 text-white py-1 text-[10px] font-bold transition';
        confirmBtn.textContent = '[ POTVRDIT ]';
        confirmBtn.onclick = function() { confirmOptimization(data.rewritten); };

        var rejectBtn = document.createElement('button');
        rejectBtn.className = 'flex-1 bg-red-900 hover:bg-red-800 text-gray-300 py-1 text-[10px] font-bold transition';
        rejectBtn.textContent = '[ ODMÍTNOUT ]';
        rejectBtn.onclick = function() { cancelOptimization(data.original); };

        btns.appendChild(confirmBtn);
        btns.appendChild(rejectBtn);
        div.appendChild(btns);
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function confirmOptimization(text) {
        var box = document.getElementById('optimizerConfirmBox');
        if (box) box.remove();
        client.send({ content: text, confirm_opt: true });
        var input = document.getElementById('msgInput');
        input.disabled = false;
        input.placeholder = t('agent_terminal.message_placeholder', 'Vložte odpověď...');
        input.focus();
    }

    function cancelOptimization(original) {
        var box = document.getElementById('optimizerConfirmBox');
        if (box) box.remove();
        var input = document.getElementById('msgInput');
        input.disabled = false;
        input.value = original;
        input.placeholder = t('agent_terminal.message_placeholder', 'Vložte odpověď...');
        input.focus();
    }

    // Globální pro onclick v HTML
    window.confirmOptimization = confirmOptimization;
    window.cancelOptimization = cancelOptimization;

    // === SYSTEM ALERT ===
    function showSystemAlert(content) {
        var overlay = document.createElement('div');
        overlay.id = 'systemAlertOverlay';
        overlay.className = 'fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4';

        var inner = document.createElement('div');
        inner.className = 'border-2 border-yellow-500 bg-black p-4 max-w-md text-center animate-pulse';

        var icon = document.createElement('div');
        icon.className = 'text-yellow-500 text-2xl mb-2';
        icon.textContent = '!';

        var msg = document.createElement('div');
        msg.className = 'text-yellow-300 text-sm font-mono whitespace-pre-line';
        msg.textContent = content;

        var btn = document.createElement('button');
        btn.className = 'mt-3 border border-yellow-500 text-yellow-500 px-4 py-1.5 text-sm hover:bg-yellow-900 transition font-mono';
        btn.textContent = '[ ROZUMÍM ]';
        btn.onclick = function() { overlay.remove(); };

        inner.appendChild(icon);
        inner.appendChild(msg);
        inner.appendChild(btn);
        overlay.appendChild(inner);
        document.body.appendChild(overlay);
        setTimeout(function() { if (overlay.parentNode) overlay.remove(); }, 10000);
        if (window.sfx) sfx.playError();
    }

    // === CHAT ===
    function appendMessage(data) {
        if (!data.content) return;
        var div = document.createElement('div');
        div.className = 'chat-bubble ' + (data.role === 'user' ? 'user self-start w-3/4' : 'agent self-end w-3/4');

        var sender = document.createElement('span');
        sender.className = 'sender';
        sender.textContent = data.sender.toUpperCase();

        var content = document.createElement('div');
        content.textContent = data.content;

        div.appendChild(sender);
        div.appendChild(content);
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // === VISIBILITY ===
    function applyHyperVisibility(mode) {
        document.body.classList.remove('mode-normal', 'mode-blackbox', 'mode-forensic', 'mode-ephemeral');
        document.body.classList.add('mode-' + mode);
    }

    function applyTemperature(temp) {
        document.body.classList.remove('instability-low', 'instability-med', 'instability-high');
        if (temp > 100 && temp <= 250) document.body.classList.add('instability-low');
        if (temp > 250 && temp <= 350) document.body.classList.add('instability-med');
        if (temp > 350) {
            document.body.classList.add('instability-high');
            if (window.sfx) sfx.playError();
        }
        var ind = document.getElementById('overloadSignal');
        if (ind) {
            if (temp > 350) ind.classList.remove('hidden');
            else ind.classList.add('hidden');
        }
    }

    // === HYPER LOCK ===
    window.toggleAutopilot = function() {
        var toggle = document.getElementById('autopilotToggle');
        if (toggle.checked) {
            document.getElementById('hyperLockOverlay').classList.remove('hidden');
            client.send({ type: 'autopilot_toggle', active: true });
        } else {
            client.send({ type: 'autopilot_toggle', active: false });
        }
    };

    window.attemptUnlock = function() {
        var pass = document.getElementById('unlockPass').value;
        if (pass === currentUsername || pass === "master_control_666") {
            document.getElementById('hyperLockOverlay').classList.add('hidden');
            document.getElementById('autopilotToggle').checked = false;
            document.getElementById('unlockPass').value = "";
            client.send({ type: 'autopilot_toggle', active: false });
        } else {
            alert('PŘÍSTUP ODEPŘEN');
            if (window.sfx) sfx.playError();
        }
    };

    // === TYPING ===
    var typingTimeout = null;
    document.getElementById('msgInput').addEventListener('input', function() {
        if (!typingTimeout) client.send({ type: 'typing_start', session_id: currentSessionId });
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(function() {
            client.send({ type: 'typing_stop', session_id: currentSessionId });
            typingTimeout = null;
        }, 1000);
    });

    function showTypingIndicator(show) {
        var indicator = document.getElementById('typingIndicator');
        if (show) {
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.id = 'typingIndicator';
                indicator.className = 'text-[10px] text-green-500 italic ml-1 animate-pulse';
                indicator.textContent = t('agent_terminal.typing_indicator', '>> UŽIVATEL PÍŠE...');
                chatHistory.appendChild(indicator);
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
        } else {
            if (indicator) indicator.remove();
        }
    }
})();
