import WebSocketManager from './WebSocketManager.js';

const wsManager = WebSocketManager;
wsManager.connect(gameId);

const [container] = document.getElementsByClassName('container');
const currentTemplate = container.getAttribute('data-template');

// TODO: This works, but it's kinda gross. Rethink!
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
} else if (currentTemplate === 'hand') {
    wsManager.registerHandler('hand', (data) => {
        if (data.chosen_word) window.location.reload();
    });
} else if (currentTemplate === 'check') {
    wsManager.registerHandler('check', (data) => {
        if (data.new_guess) {
            const checks = document.querySelector("#guesses_to_check")
            const field = document.createElement('fieldset')

            const content = `
                    <label>${data.new_guess.word} means: ${ data.new_guess.content }</label>
                    <select id="${data.new_guess.id}" name="${data.new_guess.id}">
                        <option value="False">Ok</option>
                        <option value="True">Remove</option>
                    </select>
            `;
            
            field.innerHTML = content
            checks.appendChild(field)
        }
    })
} else if (currentTemplate === 'guesses') {
    wsManager.registerHandler('guesses', (data) => {
        if (data.guesses_ready) window.location.reload();
    });
} else if (currentTemplate === 'hand_detail') {
    wsManager.registerHandler('hand_detail', (data) => {
        if (data.new_vote) {
            const votes = document.querySelector("#votes");
            const new_vote = document.createElement('div');

            const content = `
                    <label>~ Vote '${data.new_vote.content}' from ${data.new_vote.votant}</label>
            `;
            
            new_vote.innerHTML = content
            votes.appendChild(new_vote)
        } else if (data.hand_finished) {
            window.location.reload();
        } else if (data.url) {
            window.location.href = data.url;
        }
    });
}
