document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const suggestions = document.getElementById('suggestions');
    const clearChatButton = document.getElementById('clear-chat');
    const themeToggle = document.getElementById('theme-toggle');

    // Tập hợp các câu trả lời mẫu
    const responses = {
        "mụn": "Mụn trứng cá là tình trạng viêm nang lông tuyến bã, thường gặp ở tuổi dậy thì. Để điều trị mụn, bạn nên: 1. Vệ sinh da mặt 2 lần/ngày với sữa rửa mặt phù hợp. 2. Sử dụng các sản phẩm chứa salicylic acid, benzoyl peroxide. 3. Tránh nặn mụn để ngừa sẹo và nhiễm trùng. 4. Thăm khám bác sĩ da liễu nếu mụn nặng.",
        "da khô": "Chăm sóc da khô cần chú ý: 1. Dưỡng ẩm ngay sau khi tắm khi da còn ẩm. 2. Sử dụng sữa rửa mặt dịu nhẹ, không chứa xà phòng. 3. Uống đủ nước (2-3 lít/ngày). 4. Tránh tắm nước quá nóng. 5. Sử dụng kem dưỡng ẩm chứa ceramide, hyaluronic acid.",
        "dị ứng": "Khi bị dị ứng mỹ phẩm: 1. Ngưng sử dụng sản phẩm ngay lập tức. 2. Rửa mặt với nước sạch. 3. Chườm lạnh để giảm sưng đỏ. 4. Sử dụng kem dưỡng ẩm dịu nhẹ. 5. Nếu triệu chứng nặng (khó thở, sưng mặt), cần đến cơ sở y tế ngay.",
        "vảy nến": "Vảy nến là bệnh da mạn tính với các mảng da đỏ, bong vảy trắng. Điều trị bao gồm: 1. Thuốc bôi corticosteroid, vitamin D3. 2. Liệu pháp ánh sáng. 3. Thuốc uống hoặc tiêm trong trường hợp nặng. 4. Giữ ẩm da, tránh căng thẳng và chấn thương da.",
        "chống nắng": "Bảo vệ da khỏi tác hại của ánh nắng: 1. Sử dụng kem chống nắng SPF 30+ hàng ngày. 2. Thoa lại sau 2-3 giờ khi hoạt động ngoài trời. 3. Mặc quần áo chống nắng, đội mũ rộng vành. 4. Tránh ánh nắng từ 10h-16h. 5. Chọn kem chống nắng phổ rộng (UVA/UVB)."
    };

    // Thêm sự kiện cho nút gửi
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Thêm sự kiện cho các gợi ý
    suggestions.querySelectorAll('.suggestion').forEach(button => {
        button.addEventListener('click', function() {
            chatInput.value = this.textContent;
            sendMessage();
        });
    });

    // Xóa cuộc trò chuyện
    clearChatButton.addEventListener('click', function() {
        if (confirm('Bạn có chắc muốn xóa toàn bộ cuộc trò chuyện?')) {
            chatMessages.innerHTML = `
                <div class="message bot">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <p>Cuộc trò chuyện đã được xóa. Tôi có thể giúp gì cho bạn?</p>
                        <div class="message-time">${getCurrentTime()}</div>
                    </div>
                </div>
            `;
        }
    });

    // Chuyển đổi chế độ sáng/tối
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('light-mode');
        const icon = this.querySelector('i');
        if (document.body.classList.contains('light-mode')) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    });

    // Hàm gửi tin nhắn
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message === '') return;

        // Thêm tin nhắn của người dùng
        addMessage(message, 'user');
        chatInput.value = '';

        // Hiển thị chỉ báo đang nhập
        showTypingIndicator();

        // Giả lập thời gian xử lý
        setTimeout(() => {
            removeTypingIndicator();
            // Tạo phản hồi
            const response = generateResponse(message);
            addMessage(response, 'bot');
        }, 1500);
    }

    // Hàm thêm tin nhắn
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const messageText = document.createElement('p');
        messageText.innerHTML = text;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = getCurrentTime();

        contentDiv.appendChild(messageText);
        contentDiv.appendChild(timeDiv);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // Hiển thị chỉ báo đang nhập
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typing-indicator';

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = 'Đang nhập<span class="typing-dots"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span>';

        contentDiv.appendChild(typingIndicator);
        typingDiv.appendChild(avatarDiv);
        typingDiv.appendChild(contentDiv);

        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    // Xóa chỉ báo đang nhập
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Tạo phản hồi dựa trên tin nhắn
    function generateResponse(message) {
        const lowerMessage = message.toLowerCase();

        // Kiểm tra từ khóa và trả về phản hồi phù hợp
        if (lowerMessage.includes('mụn') || lowerMessage.includes('trứng cá')) {
            return responses["mụn"];
        } else if (lowerMessage.includes('da khô') || lowerMessage.includes('khô da')) {
            return responses["da khô"];
        } else if (lowerMessage.includes('dị ứng') || lowerMessage.includes('mỹ phẩm')) {
            return responses["dị ứng"];
        } else if (lowerMessage.includes('vảy nến')) {
            return responses["vảy nến"];
        } else if (lowerMessage.includes('chống nắng') || lowerMessage.includes('nắng')) {
            return responses["chống nắng"];
        } else {
            return "Tôi hiểu bạn đang quan tâm về: '" + message + "'. Hiện tại tôi chuyên về tư vấn các vấn đề da liễu như mụn, da khô, dị ứng, vảy nến và chống nắng. Bạn có thể hỏi cụ thể hơn về một trong các chủ đề này không?";
        }
    }

    // Lấy thời gian hiện tại
    function getCurrentTime() {
        const now = new Date();
        return now.getHours().toString().padStart(2, '0') + ':' +
               now.getMinutes().toString().padStart(2, '0');
    }

    // Cuộn xuống cuối cùng
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});