import WebSocketManager from './WebSocketManager.js';

const wsManager = WebSocketManager;
wsManager.connect(gameId);

const [container] = document.getElementsByClassName('container');
const currentTemplate = container.getAttribute('data-template');

if (currentTemplate === 'waiting') {
    wsManager.registerHandler('waiting', (data) => {
        // If data.url has an url, then the game started...
        if (data.url) return window.location.href = data.url;

        const newUsername = data.player_username;
        const usernames = document.getElementById('usernames');

        // If the username is the same as the current user or already was added...
        if (USERNAME === newUsername || document.getElementById(newUsername)) return;

        const newItem = document.createElement('li');
        const h1Item = document.createElement('h1');

        h1Item.textContent = newUsername;
        newItem.id = newUsername;

        newItem.appendChild(h1Item);
        usernames.appendChild(newItem);
    });

    const button = document.querySelector('#start_game');
    if (button) button.onclick = function(e) {
        wsManager.send(JSON.stringify({
            'event_type': 'start_game'
        }));
    };
} else if (currentTemplate === 'hand') {
    wsManager.registerHandler('hand', (data) => {
        if (data.chosen_word) window.location.reload();
    });

    const button = document.querySelector('#choose');
    if (button) button.onclick = function(e) {
        wsManager.send(JSON.stringify({
            'event_type': 'chosen_word'
        }));
    };
}
