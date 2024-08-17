import { connectWebSocket } from "./ws.js";

connectWebSocket(
    gameId, 
    (data) => {
        const newUsername = data.player_username;
        const usernames = document.getElementById('usernames');

        // If the username is the same as the current user or already was added...
        if (username === newUsername || document.getElementById(newUsername)) return;

        const newItem = document.createElement('li');
        const h1Item = document.createElement('h1');

        h1Item.textContent = newUsername;
        newItem.id = newUsername;

        newItem.appendChild(h1Item);
        usernames.appendChild(newItem);
    },
    (chatSocket) => {
        chatSocket.send(JSON.stringify({
            'player_username': username,
            'event_type': 'player_join'
        }));
    }
);