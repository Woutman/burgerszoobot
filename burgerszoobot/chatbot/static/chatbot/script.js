document.addEventListener('DOMContentLoaded', function() {
    // Function to get the CSRF token from the cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatLog = document.getElementById('chat-log');

    sendBtn.addEventListener('click', () => {
        const message = userInput.value;

        fetch('/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: new URLSearchParams({message: message})
        })
        .then(response => response.json())
        .then(data => {
            chatLog.innerHTML += `<p class="user-message"><strong>You:</strong> ${message}</p>`;
            chatLog.innerHTML += `<p class="bot-message"><strong>Bot:</strong> ${data.response}</p>`;
            userInput.value = '';
            chatLog.scrollTop = chatLog.scrollHeight;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
})
