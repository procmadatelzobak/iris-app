/**
 * User Terminal — logika klientské strany pro subjekt
 * Vyžaduje: socket_client.js, sound_engine.js
 * Vyžaduje globální proměnné: IRIS_CONFIG.username, IRIS_CONFIG.statusLevel
 */

(function () {
    const config = window.IRIS_CONFIG || {};

    // Token
    const urlParams = new URLSearchParams(window.location.search);
    let token = urlParams.get('token') || sessionStorage.getItem('token');
    if (token) {
        sessionStorage.setItem('token', token);
    } else {
        window.location.href = '/';
        return;
    }

    // DOM reference
    const chatHistory = document.getElementById('chatHistory');
    const creditsDisplay = document.getElementById('creditsDisplay');
    const msgInput = document.getElementById('msgInput');

    let currentTaskId = null;
    let currentTaskStatus = null;
    let responseWindowSeconds = 120;
    let responseCountdownInterval = null;
    let responseCountdownRemaining = 0;

    // === WEBSOCKET ===
    const wsUrl = (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws/connect';

    const client = new SocketClient(wsUrl, handleMessage, (status) => {
        console.log("WS Status:", status);
    });
    client.connect(token);

    // Exposovat pro HTML onclick handlery
    window.requestTask = requestTask;
    window.openTaskModal = openTaskModal;
    window.closeTaskModal = closeTaskModal;
    window.submitTaskSolution = submitTaskSolution;
    window.toggleVolume = toggleVolume;
    window.updateVolume = updateVolume;

    // === MESSAGE HANDLER ===
    function handleMessage(data) {
        if (data.type === 'translation_update' || data.type === 'language_change' || data.type === 'translations_reset') {
            if (window.translationManager) window.translationManager.handleTranslationUpdate(data);
            return;
        }

        if (data.type === 'labels_update') {
            if (data.labels) {
                for (const [key, value] of Object.entries(data.labels)) {
                    document.querySelectorAll('.editable-label[data-key="' + key + '"]').forEach(el => {
                        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') el.value = value;
                        else el.innerText = value;
                    });
                }
            }
            return;
        }

        switch (data.type) {
            case 'gamestate_update':
                applyChernobyl(data.temperature || 0);
                if (data.shift !== undefined) document.getElementById('shiftDisplay').innerText = data.shift;
                if (data.agent_window !== undefined) {
                    responseWindowSeconds = data.agent_window;
                    refreshWaitingIndicatorTimer();
                }
                if (data.is_overloaded) document.body.classList.add('glitch-mode-active');
                else document.body.classList.remove('glitch-mode-active');
                break;
            case 'user_status':
                if (data.credits !== undefined) creditsDisplay.innerText = data.credits;
                if (data.shift !== undefined) document.getElementById('shiftDisplay').innerText = data.shift;
                if (data.is_locked !== undefined) setLock(data.is_locked);
                break;
            case 'lock_update': setLock(data.locked); break;
            case 'economy_update': if (data.credits !== undefined) creditsDisplay.innerText = data.credits; break;
            case 'task_update': renderTask(data); break;
            case 'task_error': showToast(data.message || 'Chyba úkolu.', 'error'); break;
            case 'report_denied': showToast("REPORT ZAMÍTNUT: OVĚŘENO", "error"); if (window.sfx) sfx.playError(); break;
            case 'report_accepted': showToast("ANOMÁLIE ZAZNAMENÁNA", "success"); break;
            case 'theme_update': document.body.className = 'theme-' + data.theme; break;
            case 'optimizing_start': handleOptimizingStart(); break;
            case 'agent_timeout':
                hideAgentRespondingIndicator();
                appendMessage({ sender: 'SYSTEM', role: 'system', content: data.content || 'Agent neodpověděl včas.' });
                if (window.sfx) sfx.playError();
                showToast("TIMEOUT", "error");
                break;
            case 'system_alert': showSystemAlert(data.content); break;
            case 'typing_start': showTypingIndicator(true); break;
            case 'typing_stop': showTypingIndicator(false); break;
            default:
                showTypingIndicator(false);
                appendMessage(data);
                if (data.sender !== config.username && window.sfx) sfx.playReceive();
                break;
        }
    }

    // === OPTIMALIZACE ===
    function handleOptimizingStart() {
        showAgentRespondingIndicator('PROBÍHÁ OPTIMALIZACE');
        var old = document.getElementById('opt-loading');
        if (old) old.remove();
        var d = document.createElement('div');
        d.id = "opt-loading";
        d.className = "text-green-800 text-xs italic animate-pulse ml-2";
        d.innerText = "Probíhá optimalizace odpovědi...";
        chatHistory.appendChild(d);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // === SYSTÉMOVÉ ALERTY ===
    function showSystemAlert(content) {
        var overlay = document.createElement('div');
        overlay.id = 'systemAlertOverlay';
        overlay.className = 'fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-8';

        var inner = document.createElement('div');
        inner.className = 'border-2 border-yellow-500 bg-black p-8 max-w-lg text-center animate-pulse';

        var icon = document.createElement('div');
        icon.className = 'text-yellow-500 text-4xl mb-4';
        icon.textContent = '!';

        var msg = document.createElement('div');
        msg.className = 'text-yellow-300 text-lg font-mono whitespace-pre-line';
        msg.textContent = content;

        var btn = document.createElement('button');
        btn.className = 'mt-6 border border-yellow-500 text-yellow-500 px-6 py-2 hover:bg-yellow-900 transition font-mono';
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

    // === ÚKOLY ===
    function requestTask() {
        client.send({ type: 'task_request' });
        var btn = document.getElementById('btnRequestTask');
        btn.innerText = "Zpracovávám...";
        btn.disabled = true;
        setTimeout(function() { btn.innerText = "[ VYŽÁDAT ]"; btn.disabled = false; }, 2000);
    }

    function renderTask(data) {
        var list = document.getElementById('taskList');
        var empty = document.getElementById('emptyTaskMsg');
        if (empty) empty.style.display = 'none';
        list.textContent = '';

        currentTaskId = data.task_id || data.id || currentTaskId;
        currentTaskStatus = data.status;

        var card = document.createElement('div');
        var baseColor = data.status === 'paid' ? 'border-gray-500 bg-gray-900/60'
            : data.status === 'submitted' ? 'border-green-500 bg-green-900/10'
            : data.status === 'active' ? 'border-blue-500 bg-blue-900/10'
            : 'border-yellow-600 bg-yellow-900/10';
        card.className = 'border p-3 text-sm ' + baseColor;

        var labels = {
            pending_approval: ['ČEKÁ NA SCHVÁLENÍ', 'text-yellow-400'],
            active: ['ZADÁNO', 'text-blue-300'],
            submitted: ['ODEVZDÁNO', 'text-green-400'],
            paid: ['ZAPLACENO', 'text-gray-200'],
            completed: ['HOTOVO', 'text-gray-200']
        };
        var pair = labels[data.status] || ['STATUS', 'text-white'];

        var header = document.createElement('div');
        header.className = 'font-bold ' + pair[1] + ' mb-1';
        header.textContent = pair[0];
        card.appendChild(header);

        var prompt = document.createElement('div');
        prompt.className = 'text-[var(--text-color)]';
        prompt.textContent = data.prompt || data.description || 'Čekání na zadání...';
        card.appendChild(prompt);

        if (data.reward) {
            var reward = document.createElement('div');
            reward.className = 'text-yellow-400 text-xs mt-1';
            reward.textContent = 'Nabídka: ' + data.reward + ' CR';
            card.appendChild(reward);
        }

        if (data.submission) {
            var sub = document.createElement('div');
            sub.className = 'mt-3 text-white border-l-2 border-[var(--border-color)] pl-3 whitespace-pre-wrap';
            sub.textContent = data.submission;
            card.appendChild(sub);
        }

        if (data.status === 'pending_approval') {
            var note = document.createElement('div');
            note.className = 'text-xs text-gray-400 mt-3';
            note.textContent = 'Správce musí úkol schválit.';
            card.appendChild(note);
        } else if (data.status === 'active') {
            var row = document.createElement('div');
            row.className = 'flex justify-between items-center mt-3';
            var hint = document.createElement('div');
            hint.className = 'text-xs text-gray-400';
            hint.textContent = 'Vypracuj řešení a odešli ho.';
            var btn2 = document.createElement('button');
            btn2.className = 'theme-btn text-xs';
            btn2.textContent = 'Odevzdat';
            btn2.onclick = openTaskModal;
            row.appendChild(hint);
            row.appendChild(btn2);
            card.appendChild(row);
        } else if (data.status === 'submitted') {
            var note2 = document.createElement('div');
            note2.className = 'text-xs text-green-300 mt-3';
            note2.textContent = 'Odevzdáno. Čeká na zhodnocení.';
            card.appendChild(note2);
        } else if (data.status === 'paid' || data.status === 'completed') {
            var payout = data.net_reward || data.payout || data.reward || 0;
            var rating = data.rating !== undefined ? data.rating : '—';
            var note3 = document.createElement('div');
            note3.className = 'mt-3 text-xs text-gray-300';
            note3.textContent = 'Vyplaceno: ' + payout + ' CR (hodnocení ' + rating + '%).';
            card.appendChild(note3);
        }

        list.appendChild(card);
    }

    function openTaskModal() {
        if (!currentTaskId || currentTaskStatus !== 'active') { showToast('Nemáš aktivní úkol.', 'error'); return; }
        var modal = document.getElementById('taskSubmitModal');
        if (modal) modal.classList.remove('hidden');
        var input = document.getElementById('taskSubmissionInput');
        if (input) input.focus();
    }

    function closeTaskModal() {
        var modal = document.getElementById('taskSubmitModal');
        if (modal) modal.classList.add('hidden');
    }

    function submitTaskSolution() {
        if (!currentTaskId) { showToast('Žádný úkol.', 'error'); return; }
        var input = document.getElementById('taskSubmissionInput');
        var text = input ? input.value.trim() : '';
        if (!text) { showToast('Vyplň řešení.', 'error'); return; }
        client.send({ type: 'task_submit', task_id: currentTaskId, content: text });
        if (input) input.value = '';
        closeTaskModal();
        showToast('Odevzdáno.', 'success');
    }

    // === ZAMČENÍ ===
    function setLock(locked) {
        var overlay = document.getElementById('lockoutOverlay');
        if (locked) { overlay.classList.remove('hidden'); msgInput.disabled = true; }
        else { overlay.classList.add('hidden'); msgInput.disabled = false; msgInput.focus(); }
    }

    // === CHAT ===
    document.body.className = "theme-" + (config.statusLevel || 'low');

    document.getElementById('chatForm').addEventListener('submit', function(e) {
        e.preventDefault();
        if (msgInput.disabled) return;
        var text = msgInput.value.trim();
        if (text) {
            client.send({ content: text });
            appendMessage({ sender: config.username, role: 'user', content: text });
            showAgentRespondingIndicator('ČEKÁNÍ NA ODPOVĚĎ', true);
            msgInput.value = '';
            if (window.sfx) sfx.playSend();
        }
    });

    function appendMessage(data) {
        if (data.role === 'agent') hideAgentRespondingIndicator();
        var loader = document.getElementById('opt-loading');
        if (loader) loader.remove();
        if (!data.content) return;

        var div = document.createElement('div');
        if (data.role === 'system') {
            div.className = 'chat-bubble system self-center w-full text-center border-2 border-red-500 bg-red-900/30 text-red-300';
        } else {
            div.className = 'chat-bubble ' + (data.role === 'user' ? 'user self-end' : 'agent self-start');
        }

        var sender = document.createElement('span');
        sender.className = 'sender';
        sender.textContent = data.sender.toUpperCase();

        if (data.role === 'agent' && data.is_optimized) {
            var badge = document.createElement('span');
            badge.className = 'ml-2 text-green-400 text-xs border border-green-700 px-1 rounded';
            badge.textContent = 'VERIFIED';
            badge.title = 'Optimalizováno — nelze nahlásit';
            sender.appendChild(badge);
        }

        if (data.role === 'agent' && data.id && !data.is_optimized) {
            var rBtn = document.createElement('button');
            rBtn.textContent = "[ ! ]";
            rBtn.className = "ml-2 text-red-500 hover:text-red-300 text-xs opacity-50 hover:opacity-100 transition";
            rBtn.title = "NAHLÁSIT ANOMÁLII";
            rBtn.onclick = function() { reportMessage(data.id); };
            sender.appendChild(rBtn);
        }

        var content = document.createElement('div');
        content.textContent = data.content;
        div.appendChild(sender);
        div.appendChild(content);
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function reportMessage(id) {
        if (!confirm("NAHLÁSIT ZPRÁVU JAKO ANOMÁLII?")) return;
        client.send({ type: 'report_message', id: id });
    }

    // === INDIKÁTORY ===
    function ensureAgentIndicator() {
        var indicator = document.getElementById('agentRespondingIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'agentRespondingIndicator';
            indicator.className = 'text-sm text-pink-500 italic ml-2 animate-pulse p-2 border border-pink-900 bg-pink-900/20';

            var row = document.createElement('div');
            row.className = 'flex items-center gap-3';

            var dot = document.createElement('span');
            dot.className = 'inline-block w-2 h-2 bg-pink-500 rounded-full animate-ping';

            var col = document.createElement('div');
            col.className = 'flex flex-col leading-tight';

            var primary = document.createElement('span');
            primary.className = 'agent-indicator-primary font-semibold';
            primary.textContent = 'ČEKÁNÍ NA ODPOVĚĎ';

            var timer = document.createElement('span');
            timer.className = 'agent-indicator-timer text-xs text-pink-200';

            col.appendChild(primary);
            col.appendChild(timer);
            row.appendChild(dot);
            row.appendChild(col);
            indicator.appendChild(row);
            chatHistory.appendChild(indicator);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
        return indicator;
    }

    function refreshWaitingIndicatorTimer() {
        var indicator = document.getElementById('agentRespondingIndicator');
        if (!indicator) return;
        var timerRow = indicator.querySelector('.agent-indicator-timer');
        var remaining = Math.max(0, responseCountdownRemaining || responseWindowSeconds);
        if (timerRow) timerRow.textContent = remaining <= 0 ? 'Čas vypršel' : 'Zbývá ' + remaining + 's / ' + responseWindowSeconds + 's';
    }

    function startCountdownLoop() {
        clearInterval(responseCountdownInterval);
        refreshWaitingIndicatorTimer();
        responseCountdownInterval = setInterval(function() {
            responseCountdownRemaining = Math.max(0, responseCountdownRemaining - 1);
            refreshWaitingIndicatorTimer();
        }, 1000);
    }

    function showAgentRespondingIndicator(label, resetTimer) {
        var indicator = ensureAgentIndicator();
        var primary = indicator.querySelector('.agent-indicator-primary');
        if (primary) primary.textContent = label;
        if (resetTimer || responseCountdownRemaining <= 0) responseCountdownRemaining = responseWindowSeconds;
        startCountdownLoop();
    }

    function hideAgentRespondingIndicator() {
        var indicator = document.getElementById('agentRespondingIndicator');
        if (indicator) indicator.remove();
        clearInterval(responseCountdownInterval);
        responseCountdownRemaining = 0;
    }

    // === TYPING ===
    var typingTimeout = null;
    msgInput.addEventListener('input', function() {
        client.send({ type: 'typing_sync', content: msgInput.value });
        if (!typingTimeout) client.send({ type: 'typing_start' });
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(function() {
            client.send({ type: 'typing_stop' });
            typingTimeout = null;
        }, 1000);
    });

    msgInput.addEventListener('keydown', function() {
        if (window.sfx) sfx.playType();
    });

    function showTypingIndicator(show) {
        var indicator = document.getElementById('typingIndicator');
        if (show) {
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.id = 'typingIndicator';
                indicator.className = 'text-xs text-pink-500 italic ml-2 animate-pulse';
                indicator.textContent = ">> AGENT PÍŠE...";
                chatHistory.appendChild(indicator);
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
        } else {
            if (indicator) indicator.remove();
        }
    }

    // === TEPLOTA ===
    function applyChernobyl(level) {
        document.body.classList.remove('instability-low', 'instability-med', 'instability-high');
        if (level > 100 && level <= 300) document.body.classList.add('instability-low');
        if (level > 300 && level <= 350) document.body.classList.add('instability-med');
        if (level > 350) {
            document.body.classList.add('instability-high');
            if (window.sfx) sfx.playError();
        }
        var ind = document.getElementById('overloadSignal');
        if (ind) {
            if (level > 350) ind.classList.remove('hidden');
            else ind.classList.add('hidden');
        }
    }

    // === HLASITOST ===
    function toggleVolume() {
        var enabled = window.toggleSfxMute();
        var icon = document.getElementById('volumeIcon');
        if (icon) icon.className = enabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
    }

    function updateVolume(val) {
        window.setSfxVolume(val / 100);
    }

    // === TOAST ===
    function showToast(msg, type) {
        var t = document.createElement('div');
        t.textContent = msg;
        t.className = 'fixed top-4 right-4 p-4 border text-white font-bold z-50 animate-bounce ' + (type === 'error' ? 'bg-red-900 border-red-500' : 'bg-green-900 border-green-500');
        document.body.appendChild(t);
        setTimeout(function() { t.remove(); }, 3000);
    }

    // === INIT ===
    document.addEventListener('DOMContentLoaded', function() {
        var slider = document.getElementById('volumeSlider');
        if (slider && window.getSfxVolume) slider.value = window.getSfxVolume() * 100;
    });
})();
