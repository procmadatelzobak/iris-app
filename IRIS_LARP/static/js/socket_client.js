class SocketClient {
    constructor(url, onMessage, onStatusChange) {
        this.url = url;
        this.onMessage = onMessage;
        this.onStatusChange = onStatusChange; // 'connected', 'disconnected', 'error'
        this.ws = null;
        this.reconnectInterval = 3000;
    }

    connect(token) {
        // Append token to query params
        const wsUrl = `${this.url}?token=${token}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log("WS Connected");
            if (this.onStatusChange) this.onStatusChange('connected');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (this.onMessage) this.onMessage(data);
        };

        this.ws.onclose = () => {
            console.log("WS Disconnected. Reconnecting...");
            if (this.onStatusChange) this.onStatusChange('disconnected');
            setTimeout(() => this.connect(token), this.reconnectInterval);
        };

        this.ws.onerror = (err) => {
            console.error("WS Error", err);
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
}
