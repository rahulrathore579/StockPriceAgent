document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');
    const sendBtn = document.getElementById('send-btn');
    const exampleBtns = document.querySelectorAll('.example-btn');

    // Handle Example Buttons
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            userInput.value = btn.textContent;
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    // Handle Form Submit
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to UI
        appendMessage(message, 'user');
        userInput.value = '';
        sendBtn.disabled = true;

        // Show typing indicator
        const typingId = showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            // Remove typing indicator
            document.getElementById(typingId).remove();
            
            if (response.ok) {
                // Formatting basic markdown-like structures (bold, newlines)
                let formattedResponse = data.response
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n/g, '<br>');
                    
                appendMessage(formattedResponse, 'system');
            } else {
                appendMessage("Sorry, I encountered an error: " + (data.detail || "Unknown error"), 'system');
            }
        } catch (error) {
            document.getElementById(typingId).remove();
            appendMessage("Connection error. Please try again.", 'system');
            console.error('Error:', error);
        } finally {
            sendBtn.disabled = false;
            userInput.focus();
        }
    });

    function appendMessage(content, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message fade-in-up`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? '👤' : '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        contentDiv.innerHTML = `<p>${content}</p>`;

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        
        chatHistory.appendChild(msgDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = `message system-message fade-in-up`;
        msgDiv.id = id;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        contentDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        
        chatHistory.appendChild(msgDiv);
        scrollToBottom();
        
        return id;
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});
