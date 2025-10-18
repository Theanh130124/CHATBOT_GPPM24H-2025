class Chatbot {
    constructor() {
        this.theme = localStorage.getItem('chatbot-theme') || 'light';
        this.messages = JSON.parse(localStorage.getItem('chatbot-history')) || [];
        this.isTyping = false;
        this.currentSession = this.generateSessionId();

        this.initializeElements();
        this.bindEvents();
        this.applyTheme();
        this.loadChatHistory();
        this.initializeQuickReplies();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    initializeElements() {
        this.elements = {
            chatMessages: document.getElementById('chat-messages'),
            chatInput: document.getElementById('chat-input'),
            sendButton: document.getElementById('send-button'),
            clearChat: document.getElementById('clear-chat'),
            themeToggle: document.getElementById('theme-toggle'),
            minimizeChat: document.getElementById('minimize-chat'),
            typingIndicator: document.getElementById('typing-indicator'),
            suggestions: document.querySelectorAll('.suggestion-btn'),
            charCount: document.querySelector('.char-count')
        };
    }

    bindEvents() {
        // Send message events
        this.elements.sendButton.addEventListener('click', () => this.sendMessage());
        this.elements.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Character count
        this.elements.chatInput.addEventListener('input', () => this.updateCharCount());

        // Clear chat
        this.elements.clearChat.addEventListener('click', () => this.clearChat());

        // Theme toggle
        this.elements.themeToggle.addEventListener('click', () => this.toggleTheme());

        // Minimize chat
        if (this.elements.minimizeChat) {
            this.elements.minimizeChat.addEventListener('click', () => this.toggleMinimize());
        }

        // Quick suggestions
        this.elements.suggestions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.currentTarget.getAttribute('data-question');
                this.elements.chatInput.value = question;
                this.sendMessage();
            });
        });

        // Input actions
        this.initializeInputActions();
    }

    initializeInputActions() {
        // Camera button
        const cameraBtn = document.querySelector('.input-action-btn .fa-camera')?.closest('.input-action-btn');
        if (cameraBtn) {
            cameraBtn.addEventListener('click', () => this.uploadImage());
        }

        // Emoji button
        const emojiBtn = document.querySelector('.input-action-btn .fa-smile')?.closest('.input-action-btn');
        if (emojiBtn) {
            emojiBtn.addEventListener('click', () => this.toggleEmojiPicker());
        }
    }

    initializeQuickReplies() {
        this.quickReplies = {
            'mụn': [
                "Cách trị mụn đầu đen?",
                "Mụn viêm nên xử lý thế nào?",
                "Skincare cho da mụn?"
            ],
            'khô': [
                "Da khô bong tróc phải làm sao?",
                "Kem dưỡng ẩm nào tốt?",
                "Chăm sóc da khô vào mùa đông?"
            ],
            'dị ứng': [
                "Xử lý dị ứng mỹ phẩm?",
                "Da nhạy cảm nên dùng gì?",
                "Triệu chứng viêm da tiếp xúc?"
            ],
            'nám': [
                "Điều trị nám da mặt?",
                "Sản phẩm trị nám hiệu quả?",
                "Phòng ngừa nám tái phát?"
            ]
        };
    }

    updateCharCount() {
        const count = this.elements.chatInput.value.length;
        if (this.elements.charCount) {
            this.elements.charCount.textContent = `${count}/500`;

            if (count > 450) {
                this.elements.charCount.style.color = 'var(--warning-color)';
            } else if (count > 490) {
                this.elements.charCount.style.color = 'var(--error-color)';
            } else {
                this.elements.charCount.style.color = 'var(--text-muted)';
            }
        }
    }

    async sendMessage() {
        const message = this.elements.chatInput.value.trim();

        if (!message || this.isTyping) return;

        // Add user message
        this.addMessage(message, 'user');
        this.elements.chatInput.value = '';
        this.updateCharCount();

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await this.getBotResponse(message);

            // Remove typing indicator and add bot response
            this.hideTypingIndicator();
            this.addMessage(response, 'bot');

            // Show quick replies if applicable
            this.showQuickReplies(message);

        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.', 'bot');
            console.error('Chatbot error:', error);
        }
    }

    async getBotResponse(userMessage) {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

        const responses = {
            'mụn': `**Về vấn đề mụn trứng cá:**

🔍 **Nguyên nhân thường gặp:**
- Tăng tiết bã nhờn
- Vi khuẩn P. acnes
- Tắc nghẽn lỗ chân lông
- Yếu tố nội tiết tố

💊 **Điều trị cơ bản:**
1. **Làm sạch**: Sữa rửa mặt dịu nhẹ 2 lần/ngày
2. **Điều trị**:
   - Salicylic Acid (mụn đầu đen, mụn ẩn)
   - Benzoyl peroxide (mụn viêm)
   - Retinoid (mụn nang, mụn bọc)
3. **Dưỡng ẩm**: Kem dưỡng không gây bít tắc
4. **Chống nắng**: SPF 30+ hàng ngày

⚠️ **Lưu ý**: Tránh nặn mụn, hạn chế trang điểm nặng. Nếu mụn nặng, nên gặp bác sĩ da liễu.`,

            'khô': `**Chăm sóc da khô:**

🌿 **Nguyên tắc cơ bản:**
- Làm sạch dịu nhẹ, tránh xà phòng
- Dưỡng ẩm ngay sau khi rửa mặt
- Bảo vệ da khỏi tác nhân gây khô

💧 **Thành phần nên có:**
- Hyaluronic Acid (giữ ẩm)
- Ceramide (phục hồi hàng rào bảo vệ)
- Glycerin (dưỡng ẩm)
- Niacinamide (cải thiện hàng rào da)

🚫 **Cần tránh:**
- Nước nóng khi rửa mặt
- Sản phẩm chứa cồn khô
- Tẩy da chết quá mức

🛡️ **Bảo vệ**: Luôn dùng kem chống nắng phổ rộng`,

            'dị ứng': `**Xử lý dị ứng da:**

🆘 **Cấp cứu (nếu có):**
- Khó thở, sưng mặt/lưỡi
- Phát ban toàn thân
- Choáng váng, chóng mặt
→ **Đến bệnh viện ngay**

🏠 **Xử lý tại nhà:**
1. Ngừng ngay sản phẩm nghi ngờ
2. Rửa mặt với nước sạch
3. Chườm mát giảm ngứa
4. Uống nhiều nước

💊 **Thuốc có thể dùng:**
- Kháng histamine (theo chỉ định)
- Kem corticoid nhẹ (ngắn ngày)

🔍 **Phòng ngừa:**
- Test sản phẩm trước khi dùng
- Chọn sản phẩm lành tính, không hương liệu`,

            'nám': `**Điều trị nám da:**

🎯 **Nguyên tắc điều trị:**
1. **Chống nắng nghiêm ngặt** - Quan trọng nhất!
2. **Ức chế sản xuất melanin**
3. **Tăng tẩy tế bào chết**
4. **Chống viêm, chống oxy hóa**

💊 **Thành phần hiệu quả:**
- Hydroquinone (theo chỉ định bác sĩ)
- Vitamin C, Niacinamide
- Azelaic Acid, Tranexamic Acid
- Retinoid

☀️ **Chống nắng:**
- SPF 50+, PA++++
- Thoa lại sau 2-3 giờ
- Kết hợp kem và viên uống

⚠️ **Lưu ý**: Điều trị nám cần kiên trì 3-6 tháng. Nên khám bác sĩ để có phác đồ phù hợp.`,

            'default': `Cảm ơn bạn đã chia sẻ thông tin!

🤖 **Dựa trên mô tả của bạn, tôi có một số khuyến nghị:**

🔍 **Chăm sóc da cơ bản:**
- Làm sạch phù hợp với loại da
- Dưỡng ẩm đầy đủ
- Chống nắng nghiêm ngặt
- Tẩy da chết 1-2 lần/tuần

💡 **Lời khuyên quan trọng:**
- Uống đủ nước (2-3 lít/ngày)
- Ăn uống cân bằng, nhiều rau xanh
- Ngủ đủ giấc, giảm căng thẳng
- Tránh thức khuya, hút thuốc

⚠️ **Lưu ý y tế:**
Thông tin tôi cung cấp chỉ mang tính tham khảo. Để có chẩn đoán chính xác và phác đồ điều trị phù hợp, bạn nên đến gặp bác sĩ da liễu.

Bạn có thể mô tả chi tiết hơn về tình trạng da của mình không?`
        };

        // Find matching response
        const lowerMessage = userMessage.toLowerCase();
        for (const [key, response] of Object.entries(responses)) {
            if (lowerMessage.includes(key)) {
                return response;
            }
        }

        return responses.default;
    }

    addMessage(content, type) {
        const message = {
            id: Date.now(),
            content,
            type,
            timestamp: new Date().toLocaleTimeString('vi-VN', {
                hour: '2-digit',
                minute: '2-digit'
            }),
            session: this.currentSession
        };

        this.messages.push(message);
        this.renderMessage(message);
        this.saveChatHistory();
        this.scrollToBottom();
    }

    renderMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.type}-message`;
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${message.type === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    ${this.formatMessageContent(message.content)}
                </div>
                <div class="message-time">${message.timestamp}</div>
            </div>
        `;

        this.elements.chatMessages.appendChild(messageElement);
    }

    formatMessageContent(content) {
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/→/g, '→')
            .replace(/🔍/g, '🔍')
            .replace(/💊/g, '💊')
            .replace(/⚠️/g, '⚠️')
            .replace(/🆘/g, '🆘')
            .replace(/🏠/g, '🏠')
            .replace(/🎯/g, '🎯')
            .replace(/☀️/g, '☀️')
            .replace(/🤖/g, '🤖')
            .replace(/💡/g, '💡')
            .replace(/🌿/g, '🌿')
            .replace(/💧/g, '💧')
            .replace(/🚫/g, '🚫')
            .replace(/🛡️/g, '🛡️');
    }

    showQuickReplies(userMessage) {
        const lowerMessage = userMessage.toLowerCase();
        let quickReplies = [];

        // Find relevant quick replies
        for (const [key, replies] of Object.entries(this.quickReplies)) {
            if (lowerMessage.includes(key)) {
                quickReplies = [...quickReplies, ...replies];
            }
        }

        // If no specific replies, show general ones
        if (quickReplies.length === 0) {
            quickReplies = [
                "Các loại mụn thường gặp?",
                "Chăm sóc da dầu như thế nào?",
                "Sản phẩm cho da nhạy cảm?",
                "Chống lão hóa da?"
            ];
        }

        // Limit to 3 replies
        quickReplies = quickReplies.slice(0, 3);

        // Create quick replies container
        const quickRepliesContainer = document.createElement('div');
        quickRepliesContainer.className = 'quick-replies';
        quickRepliesContainer.innerHTML = `
            <div class="quick-replies-header">
                <span>Bạn có thể quan tâm:</span>
            </div>
            <div class="quick-replies-buttons">
                ${quickReplies.map(reply =>
                    `<button class="quick-reply-btn" data-question="${reply}">${reply}</button>`
                ).join('')}
            </div>
        `;

        this.elements.chatMessages.appendChild(quickRepliesContainer);
        this.scrollToBottom();

        // Add event listeners to quick reply buttons
        quickRepliesContainer.querySelectorAll('.quick-reply-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.target.getAttribute('data-question');
                this.elements.chatInput.value = question;
                this.sendMessage();
                quickRepliesContainer.remove();
            });
        });
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.elements.typingIndicator.classList.add('active');
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.elements.typingIndicator.classList.remove('active');
    }

    scrollToBottom() {
        setTimeout(() => {
            this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        }, 100);
    }

    clearChat() {
        if (confirm('Bạn có chắc muốn xóa toàn bộ cuộc trò chuyện?')) {
            this.messages = [];
            this.elements.chatMessages.innerHTML = '';
            localStorage.removeItem('chatbot-history');
            this.currentSession = this.generateSessionId();

            // Add welcome message back
            this.addWelcomeMessage();
        }
    }

    addWelcomeMessage() {
        const welcomeMessage = `👋 **Xin chào! Tôi là chatbot tư vấn da liễu thông minh**

Tôi có thể giúp bạn với các vấn đề về:

🎯 **Chẩn đoán sơ bộ** các bệnh da liễu thường gặp
💊 **Tư vấn điều trị** mụn, nám, tàn nhang, lão hóa
🌿 **Hướng dẫn chăm sóc da** hàng ngày
⚠️ **Xử lý dị ứng** và kích ứng da
📋 **Tư vấn sản phẩm** chăm sóc da phù hợp

Hãy chọn chủ đề bên dưới hoặc mô tả vấn đề của bạn!`;

        this.addMessage(welcomeMessage, 'bot');
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme();
        localStorage.setItem('chatbot-theme', this.theme);
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        const icon = this.elements.themeToggle.querySelector('i');
        if (icon) {
            icon.className = this.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }

    toggleMinimize() {
        const container = document.querySelector('.chatbot-container');
        container.classList.toggle('minimized');

        const icon = this.elements.minimizeChat.querySelector('i');
        if (container.classList.contains('minimized')) {
            icon.className = 'fas fa-expand';
        } else {
            icon.className = 'fas fa-minus';
        }
    }

    uploadImage() {
        // Implement image upload functionality
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleImageUpload(file);
            }
        };
        input.click();
    }

    handleImageUpload(file) {
        // Simulate image processing
        this.addMessage(`📷 Đã tải lên ảnh: ${file.name}`, 'user');
        this.showTypingIndicator();

        setTimeout(() => {
            this.hideTypingIndicator();
            this.addMessage('Tôi đã nhận được ảnh của bạn. Dựa trên hình ảnh, tôi thấy... [Phân tích hình ảnh sẽ được tích hợp sau]', 'bot');
        }, 2000);
    }

    toggleEmojiPicker() {
        // Implement emoji picker
        console.log('Emoji picker toggled');
    }

    saveChatHistory() {
        // Keep only last 100 messages
        const history = this.messages.slice(-100);
        localStorage.setItem('chatbot-history', JSON.stringify(history));
    }

    loadChatHistory() {
        if (this.messages.length === 0) {
            this.addWelcomeMessage();
        } else {
            this.messages.forEach(message => this.renderMessage(message));
            this.scrollToBottom();
        }
    }
}

// Additional CSS for quick replies
const quickRepliesCSS = `
.quick-replies {
    margin: 15px 0;
    animation: messageSlide 0.3s ease-out;
}

.quick-replies-header {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 8px;
    padding-left: 52px;
}

.quick-replies-buttons {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-left: 52px;
}

.quick-reply-btn {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    padding: 10px 16px;
    font-size: 0.9rem;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: left;
    max-width: 300px;
}

.quick-reply-btn:hover {
    background: var(--primary-color);
    color: white;
    transform: translateX(5px);
}
`;

// Inject quick replies CSS
const style = document.createElement('style');
style.textContent = quickRepliesCSS;
document.head.appendChild(style);

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new Chatbot();
});