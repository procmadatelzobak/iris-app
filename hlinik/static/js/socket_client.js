class SocketClient {
    constructor(url, onMessage, onStatusChange) {
        this.url = url;
        this.onMessage = onMessage;
        this.onStatusChange = (status) => {
            this.updateUI(status);
            if (onStatusChange) onStatusChange(status);
        };
        this.ws = null;
        this.pingInterval = null;
        this.pongTimeout = null;
        this.isExplicitlyClosed = false;

        // Reconnect s exponential backoff
        this.reconnectAttempts = 0;
        this.maxReconnectDelay = 30000; // max 30s
        this.baseReconnectDelay = 1000; // start 1s
    }

    connect(token) {
        this.token = token;
        this.isExplicitlyClosed = false;
        const wsUrl = `${this.url}?token=${token}`;

        try {
            this.ws = new WebSocket(wsUrl);
        } catch (e) {
            console.error("WS: Nelze vytvořit spojení", e);
            this.scheduleReconnect();
            return;
        }

        this.ws.onopen = () => {
            console.log("WS: Připojeno");
            this.reconnectAttempts = 0;
            if (this.onStatusChange) this.onStatusChange('connected');
            this.startHeartbeat();
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'pong') {
                    this.handlePong();
                    return;
                }
                if (this.onMessage) this.onMessage(data);
            } catch (e) {
                console.warn("WS: Chyba parsování zprávy", e);
            }
        };

        this.ws.onclose = (event) => {
            console.log(`WS: Odpojeno (kód: ${event.code})`);
            this.stopHeartbeat();

            if (this.isExplicitlyClosed) return;

            // Auth selhání — nepřipojovat znovu
            if (event.code === 1008 || event.code === 4001 || event.code === 4003) {
                console.error("WS: Autentizace selhala");
                if (this.onStatusChange) this.onStatusChange('auth_failed');
                return;
            }

            if (this.onStatusChange) this.onStatusChange('disconnected');
            this.scheduleReconnect();
        };

        this.ws.onerror = (err) => {
            console.error("WS: Chyba", err);
            if (this.onStatusChange) this.onStatusChange('error');
        };
    }

    scheduleReconnect() {
        if (this.isExplicitlyClosed) return;

        // Exponential backoff s jitter
        const delay = Math.min(
            this.baseReconnectDelay * Math.pow(2, this.reconnectAttempts) + Math.random() * 1000,
            this.maxReconnectDelay
        );
        this.reconnectAttempts++;
        console.log(`WS: Připojuji znovu za ${Math.round(delay / 1000)}s (pokus #${this.reconnectAttempts})`);

        if (this.onStatusChange) this.onStatusChange('reconnecting');
        setTimeout(() => this.connect(this.token), delay);
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn("WS: Nelze odeslat — spojení neaktivní");
        }
    }

    startHeartbeat() {
        this.stopHeartbeat();
        this.pingInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping' }));
                this.pongTimeout = setTimeout(() => {
                    console.warn("WS: Pong timeout — odpojuji");
                    this.ws.close();
                }, 5000);
            }
        }, 25000);
    }

    stopHeartbeat() {
        if (this.pingInterval) clearInterval(this.pingInterval);
        if (this.pongTimeout) clearTimeout(this.pongTimeout);
        this.pingInterval = null;
        this.pongTimeout = null;
    }

    handlePong() {
        if (this.pongTimeout) {
            clearTimeout(this.pongTimeout);
            this.pongTimeout = null;
        }
    }

    updateUI(status) {
        const indicator = document.getElementById('ws-status-indicator');
        if (!indicator) return;

        const styles = {
            connected:    { bg: '#22c55e', anim: 'none', title: 'Připojeno' },
            disconnected: { bg: '#ef4444', anim: 'pulse 2s infinite', title: 'Odpojeno' },
            reconnecting: { bg: '#f59e0b', anim: 'pulse 1s infinite', title: 'Připojuji...' },
            auth_failed:  { bg: '#a855f7', anim: 'none', title: 'Autentizace selhala' },
            error:        { bg: '#f97316', anim: 'none', title: 'Chyba spojení' },
        };

        const s = styles[status] || styles.error;
        indicator.style.backgroundColor = s.bg;
        indicator.style.animation = s.anim;
        indicator.title = s.title;
    }

    disconnect() {
        this.isExplicitlyClosed = true;
        this.stopHeartbeat();
        if (this.ws) this.ws.close();
    }
}
