// Chatbot functionality
let chatbotVisible = true;

// Chatbot DOM elements - will be initialized when DOM is ready
let chatbotSection, chatbotContainer, chatMessages, chatInput, sendChatBtn, toggleChatbotBtn, chatbotToggleText;

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize DOM elements
    chatbotSection = document.getElementById('chatbotSection');
    chatbotContainer = document.getElementById('chatbotContainer');
    chatMessages = document.getElementById('chatMessages');
    chatInput = document.getElementById('chatInput');
    sendChatBtn = document.getElementById('sendChatBtn');
    toggleChatbotBtn = document.getElementById('toggleChatbotBtn');
    chatbotToggleText = document.getElementById('chatbotToggleText');
    
    // Toggle chatbot visibility
    if (toggleChatbotBtn) {
        toggleChatbotBtn.addEventListener('click', () => {
            chatbotVisible = !chatbotVisible;
            
            if (chatbotVisible) {
                chatbotContainer.classList.remove('hidden');
                chatbotToggleText.textContent = 'Hide Chatbot';
            } else {
                chatbotContainer.classList.add('hidden');
                chatbotToggleText.textContent = 'Show Chatbot';
            }
        });
    }

    // Send message function
    async function sendMessage() {
        const question = chatInput.value.trim();
        if (!question) {
            return;
        }
        
        // Check if documentation is available
        if (!window.generatedDocumentation || window.generatedDocumentation.trim() === '') {
            addMessageToChat('Please generate documentation first before asking questions.', 'bot', true);
            return;
        }
        
        // Add user message to chat
        addMessageToChat(question, 'user');
        
        // Clear input and disable send button
        chatInput.value = '';
        sendChatBtn.disabled = true;
        sendChatBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        
        try {
            const response = await fetch('/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    documentation: window.generatedDocumentation
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to get response from chatbot');
            }
            
            // Add bot response to chat
            addMessageToChat(result.answer, 'bot');
            
        } catch (error) {
            addMessageToChat(`Sorry, I encountered an error: ${error.message}`, 'bot', true);
        } finally {
            // Re-enable send button
            sendChatBtn.disabled = false;
            sendChatBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
        }
    }

    // Add message to chat
    function addMessageToChat(message, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex items-start space-x-3 ${sender === 'user' ? 'chat-message-user' : 'chat-message-bot'}`;
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                        <i class="fas fa-user text-blue-600 dark:text-blue-400 text-sm"></i>
                    </div>
                </div>
                <div class="flex-1">
                    <div class="bg-blue-500 text-white rounded-lg p-3 shadow-sm ml-auto max-w-md">
                        <p class="text-sm">${message}</p>
                    </div>
                </div>
            `;
        } else {
            const errorClass = isError ? 'text-red-600 dark:text-red-400' : 'text-purple-600 dark:text-purple-400';
            const bgClass = isError ? 'bg-red-50 dark:bg-red-900' : 'bg-purple-100 dark:bg-purple-900';
            
            messageDiv.innerHTML = `
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 ${bgClass} rounded-full flex items-center justify-center">
                        <i class="fas fa-robot ${errorClass} text-sm"></i>
                    </div>
                </div>
                <div class="flex-1">
                    <div class="bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm">
                        <div class="text-sm text-gray-600 dark:text-gray-300 prose dark:prose-invert max-w-none chat-message">
                            ${message}
                        </div>
                    </div>
                </div>
            `;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event listeners for chatbot
    if (sendChatBtn) {
        sendChatBtn.addEventListener('click', sendMessage);
    }

    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Clear chat when new documentation is generated
    window.clearChat = function() {
        if (chatMessages) {
            chatMessages.innerHTML = `
                <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                            <i class="fas fa-robot text-purple-600 dark:text-purple-400 text-sm"></i>
                        </div>
                    </div>
                    <div class="flex-1">
                        <div class="bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm">
                            <p class="text-sm text-gray-600 dark:text-gray-300">
                                Hi! I'm your AI assistant. I can help you understand your project better. Ask me anything about the code, functions, classes, or how to use specific features!
                            </p>
                        </div>
                    </div>
                </div>
            `;
        }
    };

    // Show chatbot and enable input when documentation is ready
    window.showChatbot = function() {
        if (chatbotSection) {
            chatbotSection.classList.remove('hidden');
        }
        if (chatInput) {
            chatInput.disabled = false;
            chatInput.placeholder = 'Ask a question about your project...';
        }
        if (sendChatBtn) {
            sendChatBtn.disabled = false;
        }
    };
    
    // Hide chatbot
    window.hideChatbot = function() {
        if (chatbotSection) {
            chatbotSection.classList.add('hidden');
        }
    };
    
    // Enable chatbot input
    window.enableChatbot = function() {
        if (chatInput) {
            chatInput.disabled = false;
        }
        if (sendChatBtn) {
            sendChatBtn.disabled = false;
        }
    };
    
    // Disable chatbot input
    window.disableChatbot = function() {
        if (chatInput) {
            chatInput.disabled = true;
            chatInput.placeholder = 'Generate documentation first to ask questions...';
        }
        if (sendChatBtn) {
            sendChatBtn.disabled = true;
        }
    };
});
