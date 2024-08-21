class WebSocketManager {
    constructor() {
        if (!WebSocketManager.instance) {
            this.socket = null;
            this.handlers = {};
            WebSocketManager.instance = this;
        }
        return WebSocketManager.instance;
    }

    connect(gameId) {
        if (!this.socket || this.socket.readyState === WebSocket.CLOSED) {
            this.socket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);

            this.socket.onopen = () => {
                console.log('WebSocket connection established');
            };

            this.socket.onmessage = (event) => {
                this.handleMessage(event);
            };

            this.socket.onclose = () => {
                console.log('WebSocket connection closed');
            };
        }
    }

    handleMessage(event) {
        const data = JSON.parse(event.data);
        const [container] = document.getElementsByClassName('container');
        const template = container.getAttribute('data-template');

        if (this.handlers[template]) {
            this.handlers[template](data);
        }
    }

    registerHandler(template, handler) {
        this.handlers[template] = handler;
    }

    send(event) {
        this.socket.send(event);
    }
}

const instance = new WebSocketManager();

export default instance;
