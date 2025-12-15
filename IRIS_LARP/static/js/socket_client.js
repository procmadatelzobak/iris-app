class SocketClient {
    constructor(url, onMessage, onStatusChange) {
        this.url = url;
        this.onMessage = onMessage;
        this.onStatusChange = (status) => {
            this.updateUI(status);
            if (onStatusChange) onStatusChange(status);
        };
        this.ws = null;
        this.reconnectInterval = 3000;
        this.pingInterval = null;
        this.pongTimeout = null;
        this.isExplicitlyClosed = false;
    }

    connect(token) {
        this.isExplicitlyClosed = false;
        // Append token to query params
        const wsUrl = `${this.url}?token=${token}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log("WS Connected");
            if (this.onStatusChange) this.onStatusChange('connected');
            this.startHeartbeat();
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'pong') {
                this.handlePong();
                return;
            }
            if (this.onMessage) this.onMessage(data);
        };

        this.ws.onclose = (event) => {
            console.log(`WS Disconnected. Code: ${event.code}, Reason: ${event.reason}`);
            this.stopHeartbeat();

            if (this.isExplicitlyClosed) return;

            // Critical Fix: Do not reconnect on Policy Violation (Auth fail)
            if (event.code === 1008 || event.code === 4001 || event.code === 4003) {
                console.error("WS Auth Failure - Stopping reconnection loop.");
                if (this.onStatusChange) this.onStatusChange('auth_failed');
                return;
            }

            if (this.onStatusChange) this.onStatusChange('disconnected');
            setTimeout(() => this.connect(token), this.reconnectInterval);
        };

        this.ws.onerror = (err) => {
            console.error("WS Error", err);
            // Verify if error triggers close, if so, handled there.
            if (this.onStatusChange) this.onStatusChange('error');
        };
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn("WS not open, cannot send");
        }
    }

    startHeartbeat() {
        this.stopHeartbeat();
        // Send Ping every 30s
        this.pingInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping' }));

                // Expect Pong within 5s
                this.pongTimeout = setTimeout(() => {
                    console.warn("WS Pong Timeout - Reconnecting...");
                    this.ws.close(); // Triggers onclose -> reconnect
                }, 5000);
            }
        }, 30000);
    }

    updateUI(status) {
        const indicator = document.getElementById('ws-status-indicator');
        if (!indicator) return;

        switch (status) {
            case 'connected':
                indicator.style.backgroundColor = '#22c55e'; // Green
                indicator.style.animation = 'none';
                indicator.title = "WebSocket Status: Connected";
                break;
            case 'disconnected':
                indicator.style.backgroundColor = '#ef4444'; // Red
                indicator.style.animation = 'pulse 2s infinite';
                indicator.title = "WebSocket Status: Disconnected";
                break;
            case 'auth_failed':
                indicator.style.backgroundColor = '#a855f7'; // Purple
                indicator.style.animation = 'none';
                indicator.title = "WebSocket Status: Auth Failed (Blocked)";
                break;
            case 'error':
                indicator.style.backgroundColor = '#f97316'; // Orange
                indicator.title = "WebSocket Status: Error";
                break;
        }
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

    disconnect() {
        this.isExplicitlyClosed = true;
        this.stopHeartbeat();
        if (this.ws) this.ws.close();
    }
}
