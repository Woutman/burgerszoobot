document.addEventListener('DOMContentLoaded', function() {
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatLog = document.getElementById('chat-log');

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    function sendMessage() {
        const message = userInput.value;

        if (message === "") return;

        const useRAG = document.getElementById('rag-checkbox').checked;
        const useClassification = document.getElementById('classification-checkbox').checked;
        const useRephrasing = document.getElementById('rephrasing-checkbox').checked;
        const useReranking = document.getElementById('reranking-checkbox').checked;
        const useRepacking = document.getElementById('repacking-checkbox').checked;
        const chatHistoryEnabled = document.getElementById('enable-chat-history').checked;

        addMessage(message, 'user-message');
        userInput.value = '';

        fetch('/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                message: message,
                use_rag: useRAG, 
                use_classification: useClassification,
                use_rephrasing: useRephrasing, 
                use_reranking: useReranking, 
                use_repacking: useRepacking,  
                chat_history_enabled: chatHistoryEnabled
            })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.response, 'bot-message', true);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function addMessage(content, className, isHTML = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = className;
    
        if (isHTML) {
            messageDiv.innerHTML = content; 
        } else {
            messageDiv.textContent = content;
        }
    
        chatLog.appendChild(messageDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default behavior (form submission)
            sendMessage();
        }
    });
})
