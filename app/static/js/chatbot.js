class Chatbot {
  constructor() {
    this.theme = localStorage.getItem("chatbot-theme") || "light"
    this.isTyping = false
    this.apiBaseUrl = "/api/chat"
    this.currentConversationId = null
    this.conversations = []

    this.initializeElements()
    this.bindEvents()
    this.applyTheme()
    this.loadConversations()
  }

  initializeElements() {
    this.elements = {
      chatMessages: document.getElementById("chat-messages"),
      chatInput: document.getElementById("chat-input"),
      sendButton: document.getElementById("send-button"),
      clearChat: document.getElementById("clear-chat"),
      themeToggle: document.getElementById("theme-toggle"),
      infoBtn: document.getElementById("info-btn"),
      newChatBtn: document.getElementById("new-chat-btn"),
      clearHistoryBtn: document.getElementById("clear-history-btn"),
      chatHistory: document.getElementById("chat-history"),
      suggestionsContainer: document.getElementById("suggestions-container"),
      suggestions: document.querySelectorAll(".suggestion-btn"),
      sidebar: document.getElementById("chatbot-sidebar"),
    }
  }

  bindEvents() {
    this.elements.sendButton.addEventListener("click", () => this.sendMessage())
    this.elements.chatInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        this.sendMessage()
      }
    })

    this.elements.clearChat.addEventListener("click", () => this.clearCurrentChat())
    this.elements.themeToggle.addEventListener("click", () => this.toggleTheme())

    if (this.elements.infoBtn) {
      this.elements.infoBtn.addEventListener("click", () => {
        const infoModal = document.getElementById("infoModal")
        if (infoModal) {
          const bootstrap = window.bootstrap
          if (bootstrap) {
            const Modal = bootstrap.Modal
            new Modal(infoModal).show()
          } else {
            console.error("Bootstrap library is not loaded.")
          }
        }
      })
    }

    if (this.elements.newChatBtn) {
      this.elements.newChatBtn.addEventListener("click", () => this.startNewConversation())
    }

    if (this.elements.clearHistoryBtn) {
      this.elements.clearHistoryBtn.addEventListener("click", () => this.clearAllHistory())
    }

    this.elements.suggestions.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const topic = e.currentTarget.getAttribute("data-topic")
        this.handleSuggestion(topic)
      })
    })
  }

  handleSuggestion(topic) {
    const suggestions = {
      acne: "Tôi muốn biết cách trị mụn trứng cá hiệu quả",
      "dry-skin": "Làm sao để chăm sóc da khô bong tróc?",
      allergy: "Tôi bị dị ứng mỹ phẩm, phải làm sao?",
      psoriasis: "Bệnh vảy nến có cách điều trị nào không?",
      sunscreen: "Nên dùng kem chống nắng như thế nào?",
    }

    if (suggestions[topic]) {
      this.elements.chatInput.value = suggestions[topic]
      this.sendMessage()
    }
  }

  async loadConversations() {
    try {
      const response = await fetch(`${this.apiBaseUrl}/conversations`)
      if (!response.ok) throw new Error("Failed to load conversations")

      this.conversations = await response.json()

      // Display conversations in sidebar
      if (this.elements.chatHistory) {
        this.renderConversationsSidebar(this.conversations)
      }

      // Load first conversation or create new one
      if (this.conversations.length > 0) {
        await this.loadConversation(this.conversations[0].id)
      } else {
        await this.startNewConversation()
      }
    } catch (error) {
      console.error("Error loading conversations:", error)
      await this.startNewConversation()
    }
  }

  renderConversationsSidebar(conversations) {
    const historyContainer = this.elements.chatHistory

    if (!conversations || conversations.length === 0) {
      historyContainer.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>Chưa có cuộc trò chuyện nào</p>
        </div>
      `
      return
    }

    historyContainer.innerHTML = conversations
      .map(
        (conv) => `
          <div class="chat-item" data-conversation-id="${conv.id}">
            <div class="chat-item-icon">
              <i class="fas fa-comments"></i>
            </div>
            <div class="chat-item-content">
              <div class="chat-item-title">${conv.title}</div>
              <div class="chat-item-time">${conv.updatedAt}</div>
            </div>
          </div>
        `,
      )
      .join("")

    // Add click handlers to conversation items
    document.querySelectorAll(".chat-item").forEach((item) => {
      item.addEventListener("click", async () => {
        const convId = item.getAttribute("data-conversation-id")
        await this.loadConversation(Number.parseInt(convId))
      })
    })
  }

  async loadConversation(conversationId) {
    try {
      this.currentConversationId = conversationId
      const response = await fetch(`${this.apiBaseUrl}/conversations/${conversationId}/messages`)
      if (!response.ok) throw new Error("Failed to load messages")

      const messages = await response.json()
      this.elements.chatMessages.innerHTML = ""

      // Display all messages
      messages.forEach((msg) => {
        this.renderMessage({
          content: msg.content,
          type: msg.type,
          timestamp: msg.timestamp,
        })
      })

      this.scrollToBottom()
    } catch (error) {
      console.error("Error loading conversation:", error)
    }
  }

  async startNewConversation() {
    try {
      const response = await fetch(`${this.apiBaseUrl}/conversations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: `Cuộc trò chuyện ${new Date().toLocaleString("vi-VN")}`,
        }),
      })

      if (!response.ok) throw new Error("Failed to create conversation")

      const newConversation = await response.json()
      this.currentConversationId = newConversation.id
      this.conversations.unshift(newConversation)

      // Update sidebar
      if (this.elements.chatHistory) {
        this.renderConversationsSidebar(this.conversations)
      }

      this.elements.chatMessages.innerHTML = ""
      this.addWelcomeMessage()
    } catch (error) {
      console.error("Error creating conversation:", error)
    }
  }

  async sendMessage() {
    const message = this.elements.chatInput.value.trim()

    if (!message || this.isTyping) return

    // Create conversation if not exists
    if (!this.currentConversationId) {
      await this.startNewConversation()
    }

    this.addMessageToUI(message, "user")
    this.elements.chatInput.value = ""

    // Save user message to database
    try {
      await this.saveMessageToDatabase(message, "user")
    } catch (error) {
      console.error("Error saving user message:", error)
    }

    this.showTypingIndicator()

    try {
      const botResponse = await this.getBotResponse(message)
      this.hideTypingIndicator()
      this.addMessageToUI(botResponse, "bot")

      // Save bot response to database
      await this.saveMessageToDatabase(botResponse, "bot")
    } catch (error) {
      this.hideTypingIndicator()
      const errorMsg = "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau."
      this.addMessageToUI(errorMsg, "bot")
      console.error("Chatbot error:", error)
    }
  }

  async saveMessageToDatabase(content, type) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/conversations/${this.currentConversationId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: content,
          type: type,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to save message")
      }
    } catch (error) {
      console.error("Error saving message to database:", error)
    }
  }

  async getBotResponse(userMessage) {
    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 1500))

    const responses = {
      mụn: `**Về vấn đề mụn trứng cá:**

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

⚠️ **Lưu ý**: Tránh nặn mụ, hạn chế trang điểm nặng. Nếu mụn nặng, nên gặp bác sĩ da liễu.`,

      khô: `**Chăm sóc da khô:**

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

      "dị ứng": `**Xử lý dị ứng da:**

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

      nám: `**Điều trị nám da:**

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
- Dùng hàng ngày, kể cả ngày mưa

⚠️ **Lưu ý**: Điều trị nám cần kiên trì 3-6 tháng. Nên khám bác sĩ để có phác đồ phù hợp.`,

      nắng: `**Chống nắng cho da:**

☀️ **Tại sao cần chống nắng:**
- Ngăn ngừa ung thư da
- Phòng lão hóa da sớm
- Giảm nám, tàn nhang
- Bảo vệ hàng rào da

🛡️ **Chỉ số SPF:**
- SPF 30: Chặn 97% tia UV
- SPF 50: Chặn 98% tia UV
- SPF 50+: Chặn 99%+ tia UV

📋 **Cách sử dụng đúng:**
1. Thoa đủ lượng (1/4 thìa cà phê cho mặt)
2. Thoa 15 phút trước khi ra nắng
3. Thoa lại mỗi 2-3 giờ
4. Dùng hàng ngày, kể cả ngày mưa

💡 **Lời khuyên:**
- Kết hợp kem và viên uống
- Tránh nắng 10-16h
- Mặc quần áo che phủ`,

      default: `Cảm ơn bạn đã chia sẻ thông tin!

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
Thông tin tôi cung cấp chỉ mang tính tham khảo. Để có chẩn đoán chính xác, bạn nên đến gặp bác sĩ da liễu.

Bạn có thể mô tả chi tiết hơn về tình trạng da của mình không?`,
    }

    const lowerMessage = userMessage.toLowerCase()
    for (const [key, response] of Object.entries(responses)) {
      if (key !== "default" && lowerMessage.includes(key)) {
        return response
      }
    }

    return responses.default
  }

  addMessageToUI(content, type) {
    const timestamp = new Date().toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    })

    this.renderMessage({
      content,
      type,
      timestamp,
    })

    this.scrollToBottom()
  }

  renderMessage(message) {
    const messageElement = document.createElement("div")
    messageElement.className = `message ${message.type}`
    messageElement.innerHTML = `
      <div class="message-avatar">
        <i class="fas fa-${message.type === "user" ? "user" : "robot"}"></i>
      </div>
      <div class="message-content">
        ${this.formatMessageContent(message.content)}
        <div class="message-time">${message.timestamp}</div>
      </div>
    `

    this.elements.chatMessages.appendChild(messageElement)
  }

  formatMessageContent(content) {
    return content
      .replace(/\n/g, "<br>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/→/g, "→")
      .replace(/🔍/g, "🔍")
      .replace(/💊/g, "💊")
      .replace(/⚠️/g, "⚠️")
      .replace(/🆘/g, "🆘")
      .replace(/🏠/g, "🏠")
      .replace(/🎯/g, "🎯")
      .replace(/☀️/g, "☀️")
      .replace(/🤖/g, "🤖")
      .replace(/💡/g, "💡")
      .replace(/🌿/g, "🌿")
      .replace(/💧/g, "💧")
      .replace(/🚫/g, "🚫")
      .replace(/🛡️/g, "🛡️")
      .replace(/📋/g, "📋")
  }

  showTypingIndicator() {
    this.isTyping = true
    const typingElement = document.createElement("div")
    typingElement.className = "message bot loading"
    typingElement.id = "typing-indicator"
    typingElement.innerHTML = `
      <div class="message-avatar">
        <i class="fas fa-robot"></i>
      </div>
      <div class="message-content">
        <div class="typing-indicator">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    `
    this.elements.chatMessages.appendChild(typingElement)
    this.scrollToBottom()
  }

  hideTypingIndicator() {
    this.isTyping = false
    const typingElement = document.getElementById("typing-indicator")
    if (typingElement) {
      typingElement.remove()
    }
  }

  scrollToBottom() {
    setTimeout(() => {
      this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight
    }, 100)
  }

  async clearCurrentChat() {
    if (confirm("Bạn có chắc muốn xóa cuộc trò chuyện hiện tại?")) {
      try {
        const response = await fetch(`${this.apiBaseUrl}/conversations/${this.currentConversationId}`, {
          method: "DELETE",
        })

        if (!response.ok) throw new Error("Failed to delete conversation")

        this.conversations = this.conversations.filter((c) => c.id !== this.currentConversationId)

        if (this.elements.chatHistory) {
          this.renderConversationsSidebar(this.conversations)
        }

        await this.startNewConversation()
      } catch (error) {
        console.error("Error deleting conversation:", error)
      }
    }
  }

  async clearAllHistory() {
    if (confirm("Bạn có chắc muốn xóa tất cả lịch sử trò chuyện? Hành động này không thể hoàn tác.")) {
      try {
        // Delete all conversations
        for (const conv of this.conversations) {
          await fetch(`${this.apiBaseUrl}/conversations/${conv.id}`, {
            method: "DELETE",
          })
        }

        this.conversations = []
        this.elements.chatMessages.innerHTML = ""

        if (this.elements.chatHistory) {
          this.renderConversationsSidebar([])
        }

        await this.startNewConversation()
      } catch (error) {
        console.error("Error clearing history:", error)
      }
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

Hãy chọn chủ đề bên dưới hoặc mô tả vấn đề của bạn!`

    this.addMessageToUI(welcomeMessage, "bot")
  }

  toggleTheme() {
    this.theme = this.theme === "light" ? "dark" : "light"
    this.applyTheme()
    localStorage.setItem("chatbot-theme", this.theme)
  }

  applyTheme() {
    document.documentElement.setAttribute("data-theme", this.theme)
    const icon = this.elements.themeToggle.querySelector("i")
    if (icon) {
      icon.className = this.theme === "light" ? "fas fa-moon" : "fas fa-sun"
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.chatbot = new Chatbot()
})
