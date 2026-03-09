document.addEventListener("DOMContentLoaded", () => {
    // 1. Inject Styles
    const style = document.createElement("style");
    style.innerHTML = `
        #bio-chatbot-widget {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 9999;
            font-family: 'Inter', sans-serif;
        }
        
        #bio-chat-toggle {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%);
            border-radius: 30px;
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.2s;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        #bio-chat-toggle:hover {
            transform: scale(1.05);
        }
        
        #bio-chat-window {
            position: absolute;
            bottom: 80px;
            right: 0;
            width: 350px;
            height: 500px;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 16px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transform-origin: bottom right;
            transform: scale(0);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        #bio-chat-window.open {
            transform: scale(1);
            opacity: 1;
        }
        
        .chat-header {
            padding: 1rem;
            background: rgba(15, 23, 42, 0.9);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-messages {
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .message {
            max-width: 80%;
            padding: 0.75rem;
            border-radius: 12px;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        
        .message.bot {
            align-self: flex-start;
            background: rgba(255,255,255,0.05);
            color: #cbd5e1;
            border-bottom-left-radius: 2px;
        }
        
        .message.user {
            align-self: flex-end;
            background: rgba(14, 165, 233, 0.2);
            color: white;
            border: 1px solid rgba(14, 165, 233, 0.4);
            border-bottom-right-radius: 2px;
        }
        
        .chat-input-area {
            padding: 1rem;
            border-top: 1px solid rgba(255,255,255,0.1);
            display: flex;
            gap: 0.5rem;
        }
        
        #chat-input {
            flex: 1;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 0.5rem;
            color: white;
            font-family: inherit;
        }
        
        #chat-send {
            background: #0ea5e9;
            border: none;
            border-radius: 8px;
            width: 36px;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Thinking animation */
        .typing-dots span {
            width: 4px;
            height: 4px;
            background: #94a3b8;
            border-radius: 50%;
            display: inline-block;
            margin: 0 2px;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
    `;
    document.head.appendChild(style);

    // 2. Inject HTML
    const widget = document.createElement("div");
    widget.id = "bio-chatbot-widget";
    widget.innerHTML = `
        <div id="bio-chat-window">
            <div class="chat-header">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.2rem;">🤖</span>
                    <div>
                        <div style="font-weight: 600; color: white;">BioAssist AI</div>
                        <div style="font-size: 0.7rem; color: #4ade80;">● Online</div>
                    </div>
                </div>
                <button id="close-chat" style="background:none; border:none; color: #94a3b8; cursor: pointer;">✕</button>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="message bot">
                    Hello! I'm BioAssist. How can I help you with your research today?
                </div>
            </div>
            <div class="chat-input-area">
                <input type="text" id="chat-input" placeholder="Ask about targets, protocols...">
                <button id="chat-send">➤</button>
            </div>
        </div>
        <div id="bio-chat-toggle">
            <span style="font-size: 1.5rem;">💬</span>
        </div>
    `;
    document.body.appendChild(widget);

    // 3. Logic
    const toggle = document.getElementById("bio-chat-toggle");
    const window = document.getElementById("bio-chat-window");
    const close = document.getElementById("close-chat");
    const input = document.getElementById("chat-input");
    const send = document.getElementById("chat-send");
    const messages = document.getElementById("chat-messages");

    function toggleChat() {
        window.classList.toggle("open");
    }

    toggle.addEventListener("click", toggleChat);
    close.addEventListener("click", toggleChat);

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        // User Msg
        addMessage(text, "user");
        input.value = "";

        // Bot Thinking
        const loadingId = addMessage(`<div class="typing-dots"><span style="animation-delay:-0.32s"></span><span style="animation-delay:-0.16s"></span><span></span></div>`, "bot");

        try {
            const res = await fetch("http://127.0.0.1:8000/api/chat/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    context: document.title // Send page title as context
                })
            });

            if (res.ok) {
                const data = await res.json();
                removeMessage(loadingId);
                simulateTypewriter(data.response);
            } else {
                removeMessage(loadingId);
                addMessage("⚠️ I'm having trouble connecting to the Neural Net. Please try again.", "bot");
            }
        } catch (e) {
            removeMessage(loadingId);
            addMessage("⚠️ Network Error.", "bot");
            console.error(e);
        }
    }

    send.addEventListener("click", sendMessage);
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    function addMessage(html, type) {
        const div = document.createElement("div");
        div.className = `message ${type}`;
        div.innerHTML = html;
        div.id = "msg-" + Date.now();
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div.id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function simulateTypewriter(text) {
        const div = document.createElement("div");
        div.className = `message bot`;
        messages.appendChild(div);

        let i = 0;
        const speed = 10;

        function type() {
            if (i < text.length) {
                div.textContent += text.charAt(i);
                i++;
                messages.scrollTop = messages.scrollHeight;
                setTimeout(type, speed);
            }
        }
        type();
    }
});
