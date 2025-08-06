const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');

// Load chat history from localStorage
function loadChatHistory() {
    const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
    history.forEach(msg => addMessage(msg.text, msg.isUser, false));
}

// Save a message to localStorage
function saveMessage(message, isUser) {
    const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
    history.push({ text: message, isUser });
    localStorage.setItem('chatHistory', JSON.stringify(history));
}

function clearChatHistory() {
    localStorage.removeItem('chatHistory');
    chatMessages.innerHTML = '';
}

function addMessage(message, isUser, save = true) {
    // Create a flex wrapper for alignment
    const wrapper = document.createElement('div');
    wrapper.style.display = 'flex';
    wrapper.style.justifyContent = isUser ? 'flex-end' : 'flex-start';
    wrapper.style.width = '100%';

    const messageDiv = document.createElement('div');
    messageDiv.className = `message mb-2 ${isUser ? 'user' : 'bot'}`;
    // For bot messages, allow HTML (for links)
    if (isUser) {
        messageDiv.textContent = message;
    } else {
        messageDiv.innerHTML = message;
    }
    // Style user and bot messages
    if (isUser) {
        messageDiv.style.alignSelf = 'flex-end';
        messageDiv.style.background = 'var(--primary-100, #e3f0ff)';
        messageDiv.style.color = '#222';
        messageDiv.style.borderRadius = '16px 16px 4px 16px';
        messageDiv.style.padding = '10px 14px';
        messageDiv.style.display = 'inline-block';
        messageDiv.style.minWidth = '48px';
        messageDiv.style.maxWidth = '60%';
        messageDiv.style.textAlign = 'right';
        messageDiv.style.boxShadow = '0 2px 8px rgba(80,160,255,0.10)';
        messageDiv.style.fontWeight = '500';
        messageDiv.style.fontSize = '1.1rem';
        messageDiv.style.marginRight = '0.5rem';
        messageDiv.style.marginLeft = '2rem';
        messageDiv.style.padding = '10px 16px';
    } else {
        messageDiv.style.alignSelf = 'flex-start';
        messageDiv.style.background = 'var(--primary-50, #f6fafd)';
        messageDiv.style.color = '#333';
        messageDiv.style.borderRadius = '16px 16px 16px 4px';
        messageDiv.style.padding = '10px 14px';
        messageDiv.style.maxWidth = '75%';
        messageDiv.style.textAlign = 'left';
    }
    wrapper.appendChild(messageDiv);
    chatMessages.appendChild(wrapper);
    // Save to localStorage unless told not to
    if (save) saveMessage(message, isUser);
    // Always scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

let lastTopic = null;
let userFacts = JSON.parse(localStorage.getItem('userFacts') || '{}');

function extractUserFacts(message) {
    // Simple extraction for name, mood, activity
    let updated = false;
    const nameMatch = message.match(/my name is ([a-zA-Z\u00C0-\u017F ]+)/i);
    if (nameMatch) {
        userFacts.name = nameMatch[1].trim();
        updated = true;
    }
    const moodMatch = message.match(/i feel ([a-zA-Z\u00C0-\u017F ]+)/i);
    if (moodMatch) {
        userFacts.mood = moodMatch[1].trim();
        updated = true;
    }
    const likeMatch = message.match(/i like ([a-zA-Z\u00C0-\u017F ]+)/i);
    if (likeMatch) {
        userFacts.favorite = likeMatch[1].trim();
        updated = true;
    }
    if (updated) {
        localStorage.setItem('userFacts', JSON.stringify(userFacts));
    }
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    addMessage(message, true);
    extractUserFacts(message);
    chatInput.value = '';
    try {
        const response = await fetch('/chatbot/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, last_topic: lastTopic, user_facts: userFacts })
        });
        if (response.ok) {
            const data = await response.json();
            addMessage(data.reply, false);
            lastTopic = data.topic || lastTopic;
            if (data.user_facts) {
                userFacts = data.user_facts;
                localStorage.setItem('userFacts', JSON.stringify(userFacts));
            }
        } else {
            addMessage('Sorry, something went wrong. Please try again.', false);
        }
    } catch (error) {
        addMessage('Sorry, I could not connect to the server.', false);
    }
}



// Add event listeners
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
});

// Add click event for send button
const sendButton = document.querySelector('.send-button');
if (sendButton) {
    sendButton.addEventListener('click', sendMessage);
}

// Initial welcome message
window.onload = function() {
    addMessage('Hi there! I\'m here to support you. How can I help you today?', false);
};
