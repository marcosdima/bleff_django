export function connectWebSocket(gameId, onMessageCallback = (data) => {}, onOpenCallback = () => {}) {
    const socket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);

    socket.onopen = function() {
        onOpenCallback(socket)
        console.log(`Connected to WebSocket: Game ${gameId}`);
    };

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        onMessageCallback(data);
    };

    socket.onclose = function(e) {
        console.error('WebSocket closed unexpectedly');
    };

    return socket;
}