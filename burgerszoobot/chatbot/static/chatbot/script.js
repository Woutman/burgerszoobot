document.addEventListener('DOMContentLoaded', function() {
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatLog = document.getElementById('chat-log');

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    sendBtn.addEventListener('click', () => {
        const message = userInput.value;

        fetch('/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({message: message})
        })
        .then(response => response.json())
        .then(data => {
            chatLog.innerHTML += `<p class="user-message">${message}</p>`;
            chatLog.innerHTML += `<p class="bot-message">${data.response}</p>`;
            userInput.value = '';
            chatLog.scrollTop = chatLog.scrollHeight;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
})
