const roomName = JSON.parse(document.getElementById('room-name').textContent);
const username = JSON.parse(document.getElementById('username').textContent);
const auth_group = JSON.parse(document.getElementById('auth_group').textContent);

const chatSocket = new WebSocket('ws://'+ window.location.host+ '/ws/'+roomName+ '/'
);

chatSocket.onopen = function(e) {
    chatSocket.send(JSON.stringify({
        'message': 'Joined room',
        'sender': username, // Include sender's username
        'auth_group': auth_group // Include sender's auth group
    }));
};
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const chatLog = document.querySelector('#chat-log');
    if(data.auth_group==='instructor'){
        chatLog.value += (data.sender + ' (TEACHER ): ' + data.message + '\n'); 
    }
    else{
        chatLog.value += (data.sender + ': ' + data.message + '\n');
    }
    chatLog.scrollTop = chatLog.scrollHeight;
};

// when user closes the chat window
window.onbeforeunload = function() {
    chatSocket.send(JSON.stringify({
        'message': 'Left room',
        'sender': username, // Include sender's username
        'auth_group': auth_group // Include sender's auth group
    }));
    chatSocket.close();
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};


document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': message,
        'sender': username, // Include sender's username
        'auth_group': auth_group // Include sender's auth group
    }));
    messageInputDom.value = '';
};