
(function() {
    // LifeBot Configuration
    window.LifeBotConfig = {
        botId: 1,
        botName: "Sales",
        botType: "Lead Capturing Bot",
        primaryColor: "#3B82F6",
        position: "bottom-right",
        greeting: "Hi! I'm Bot 1, your retail bot assistant. How can I help you today?",
        apiUrl: "http://localhost:8000"
    };
    
    // Create chatbot container
    const createChatbot = () => {
        const chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'lifebot-chatbot';
        chatbotContainer.innerHTML = `
            <div id="lifebot-widget" style="
                position: fixed;
                bottom: 20px; right: 20px;
                z-index: 9999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            ">
                <div id="lifebot-button" style="
                    width: 56px;
                    height: 56px;
                    background-color: #3B82F6;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    transition: transform 0.2s;
                " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                        <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
                    </svg>
                </div>
                <div id="lifebot-chat" style="
                    display: none;
                    width: 320px;
                    height: 400px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 8px 28px rgba(0,0,0,0.12);
                    position: absolute;
                    bottom: 70px;
                    right: 0;
                    overflow: hidden;
                ">
                    <div style="
                        background: #3B82F6;
                        color: white;
                        padding: 16px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                    ">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 32px; height: 32px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                                    <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
                                </svg>
                            </div>
                            <div>
                                <div style="font-weight: 500; font-size: 14px;">Sales</div>
                                <div style="font-size: 12px; opacity: 0.8;">Online</div>
                            </div>
                        </div>
                        <button id="lifebot-close" style="
                            background: none;
                            border: none;
                            color: white;
                            cursor: pointer;
                            padding: 4px;
                            border-radius: 4px;
                        " onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                    <div id="lifebot-messages" style="
                        height: 280px;
                        overflow-y: auto;
                        padding: 16px;
                        background: #f8f9fa;
                    ">
                        <div style="
                            background: white;
                            padding: 12px;
                            border-radius: 8px;
                            margin-bottom: 12px;
                            max-width: 80%;
                            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                        ">
                            Hi! I'm Bot 1, your retail bot assistant. How can I help you today?
                        </div>
                    </div>
                    <div style="
                        padding: 16px;
                        border-top: 1px solid #e9ecef;
                        display: flex;
                        gap: 8px;
                    ">
                        <input id="lifebot-input" type="text" placeholder="Type your message..." style="
                            flex: 1;
                            padding: 8px 12px;
                            border: 1px solid #ddd;
                            border-radius: 20px;
                            outline: none;
                            font-size: 14px;
                        ">
                        <button id="lifebot-send" style="
                            background: #3B82F6;
                            color: white;
                            border: none;
                            border-radius: 50%;
                            width: 36px;
                            height: 36px;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22,2 15,22 11,13 2,9"></polygon>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(chatbotContainer);

        // Event listeners
        const button = document.getElementById('lifebot-button');
        const chat = document.getElementById('lifebot-chat');
        const closeBtn = document.getElementById('lifebot-close');
        const input = document.getElementById('lifebot-input');
        const sendBtn = document.getElementById('lifebot-send');
        const messages = document.getElementById('lifebot-messages');

        button.addEventListener('click', () => {
            chat.style.display = chat.style.display === 'none' ? 'block' : 'none';
        });

        closeBtn.addEventListener('click', () => {
            chat.style.display = 'none';
        });

        const sendMessage = () => {
            const message = input.value.trim();
            if (!message) return;

            // Add user message
            const userMsg = document.createElement('div');
            userMsg.style.cssText = `
                background: #3B82F6;
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                margin: 8px 0;
                max-width: 80%;
                margin-left: auto;
                text-align: right;
            `;
            userMsg.textContent = message;
            messages.appendChild(userMsg);

            input.value = '';
            messages.scrollTop = messages.scrollHeight;

            // Send message to LifeBot API
            fetch('http://localhost:8000/chat/1', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                const botMsg = document.createElement('div');
                botMsg.style.cssText = `
                    background: white;
                    padding: 12px;
                    border-radius: 8px;
                    margin: 8px 0;
                    max-width: 80%;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                `;
                botMsg.textContent = data.response || "Thanks for your message! I'm processing your request.";
                messages.appendChild(botMsg);
                messages.scrollTop = messages.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
                const botMsg = document.createElement('div');
                botMsg.style.cssText = `
                    background: white;
                    padding: 12px;
                    border-radius: 8px;
                    margin: 8px 0;
                    max-width: 80%;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                `;
                botMsg.textContent = "Sorry, I'm having trouble connecting. Please try again later.";
                messages.appendChild(botMsg);
                messages.scrollTop = messages.scrollHeight;
            });
        };

        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createChatbot);
    } else {
        createChatbot();
    }
})();
