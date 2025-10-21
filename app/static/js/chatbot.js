// static/js/chatbot.js
class Chatbot {
  constructor() {
    this.theme = localStorage.getItem("chatbot-theme") || "light"
    this.isTyping = false
    this.apiBaseUrl = "/api/chat"
    this.currentConversationId = null
    this.conversations = []
    this.currentImageData = null

    this.initializeElements()
    this.bindEvents()
    this.applyTheme()
    this.loadConversations()
    this.setupImageUpload()
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

  setupImageUpload() {
    // Create hidden file input
    if (!document.getElementById('image-upload')) {
      const fileInput = document.createElement('input')
      fileInput.type = 'file'
      fileInput.id = 'image-upload'
      fileInput.accept = 'image/*'
      fileInput.style.display = 'none'
      document.body.appendChild(fileInput)
    }

    // Create image upload button
    if (!document.getElementById('image-upload-btn')) {
      const uploadBtn = document.createElement('button')
      uploadBtn.type = 'button'
      uploadBtn.id = 'image-upload-btn'
      uploadBtn.className = 'btn btn-outline-secondary'
      uploadBtn.title = 'Tải lên hình ảnh'
      uploadBtn.innerHTML = '<i class="fas fa-camera"></i>'

      const inputGroup = document.querySelector('.input-group')
      if (inputGroup) {
        inputGroup.insertBefore(uploadBtn, inputGroup.firstChild)
      }
    }

    // Create image preview container
    if (!document.getElementById('image-preview')) {
      const previewDiv = document.createElement('div')
      previewDiv.id = 'image-preview'
      previewDiv.style.display = 'none'
      previewDiv.style.marginTop = '10px'

      const inputContainer = document.querySelector('.chat-input-container')
      if (inputContainer) {
        inputContainer.appendChild(previewDiv)
      }
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

    if (this.elements.themeToggle) {
      this.elements.themeToggle.addEventListener("click", () => this.toggleTheme())
    }

    // Image upload events
    const uploadBtn = document.getElementById('image-upload-btn')
    const fileInput = document.getElementById('image-upload')

    if (uploadBtn && fileInput) {
      uploadBtn.addEventListener('click', () => fileInput.click())
      fileInput.addEventListener('change', (e) => this.handleImageUpload(e))
    }

    if (this.elements.infoBtn) {
      this.elements.infoBtn.addEventListener("click", () => {
        const infoModal = document.getElementById("infoModal")
        if (infoModal && window.bootstrap) {
          new window.bootstrap.Modal(infoModal).show()
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

  handleImageUpload(event) {
    const file = event.target.files[0]
    if (!file) return

    // Validate file type
    if (!file.type.match('image.*')) {
      alert('Vui lòng chọn file hình ảnh (JPEG, PNG, etc.)')
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Kích thước file không được vượt quá 5MB')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      this.currentImageData = e.target.result
      this.showImagePreview(e.target.result)
    }
    reader.onerror = () => {
      alert('Có lỗi xảy ra khi đọc file. Vui lòng thử lại.')
    }
    reader.readAsDataURL(file)
  }

  showImagePreview(imageData) {
    const previewDiv = document.getElementById('image-preview')
    if (!previewDiv) return

    previewDiv.innerHTML = `
      <div class="image-preview-container">
        <img src="${imageData}" alt="Preview" class="img-thumbnail" style="max-width: 100px; max-height: 100px;">
        <button type="button" class="btn-remove-image btn btn-sm btn-danger">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `
    previewDiv.style.display = 'block'

    // Add remove button event
    const removeBtn = previewDiv.querySelector('.btn-remove-image')
    if (removeBtn) {
      removeBtn.addEventListener('click', () => this.clearImagePreview())
    }
  }

  clearImagePreview() {
    this.currentImageData = null
    const previewDiv = document.getElementById('image-preview')
    const fileInput = document.getElementById('image-upload')

    if (previewDiv) {
      previewDiv.style.display = 'none'
      previewDiv.innerHTML = ''
    }

    if (fileInput) {
      fileInput.value = ''
    }
  }

  handleSuggestion(topic) {
    const suggestions = {
      acne: "Cách trị mụn trứng cá hiệu quả",
      "dry-skin": "Chăm sóc da khô đúng cách",
      allergy: "Xử lý dị ứng mỹ phẩm",
      psoriasis: "Điều trị bệnh vảy nến",
      sunscreen: "Sử dụng kem chống nắng hiệu quả"
    }

    if (this.elements.chatInput) {
      this.elements.chatInput.value = suggestions[topic] || topic
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
    if (!historyContainer) return

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
          <div class="chat-item ${conv.id === this.currentConversationId ? 'active' : ''}"
               data-conversation-id="${conv.id}">
            <div class="chat-item-icon">
              <i class="fas fa-comments"></i>
            </div>
            <div class="chat-item-content">
              <div class="chat-item-title">${this.escapeHtml(conv.title)}</div>
              <div class="chat-item-time">${this.escapeHtml(conv.updatedAt)}</div>
            </div>
            <button class="delete-conversation" data-id="${conv.id}" title="Xóa cuộc trò chuyện">
              <i class="fas fa-times"></i>
            </button>
          </div>
        `
      )
      .join("")

    // Add click handlers to conversation items
    document.querySelectorAll(".chat-item").forEach((item) => {
      item.addEventListener("click", async (e) => {
        if (!e.target.closest('.delete-conversation')) {
          const convId = item.getAttribute("data-conversation-id")
          await this.loadConversation(Number.parseInt(convId))
        }
      })
    })

    // Add delete conversation handlers
    document.querySelectorAll(".delete-conversation").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation()
        const convId = btn.getAttribute("data-id")
        await this.deleteConversation(Number.parseInt(convId))
      })
    })
  }

  async deleteConversation(conversationId) {
    if (!confirm('Bạn có chắc muốn xóa cuộc trò chuyện này?')) return

    try {
      const response = await fetch(`/api/chat/conversations/${conversationId}`, {
        method: 'DELETE'
      })

      if (!response.ok) throw new Error('Failed to delete conversation')

      if (this.currentConversationId === conversationId) {
        await this.startNewConversation()
      }

      await this.loadConversations()
    } catch (error) {
      console.error('Error deleting conversation:', error)
      alert('Có lỗi xảy ra khi xóa cuộc trò chuyện')
    }
  }

  async loadConversation(conversationId) {
    try {
      this.currentConversationId = conversationId
      const response = await fetch(`${this.apiBaseUrl}/conversations/${conversationId}/messages`)
      if (!response.ok) throw new Error("Failed to load messages")

      const messages = await response.json()

      if (this.elements.chatMessages) {
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
        await this.loadConversations() // Refresh sidebar for active state
      }
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

      if (this.elements.chatMessages) {
        this.elements.chatMessages.innerHTML = ""
        this.addWelcomeMessage()
      }
    } catch (error) {
      console.error("Error creating conversation:", error)
    }
  }

  async sendMessage() {
    const message = this.elements.chatInput?.value.trim() || ''
    const imageData = this.currentImageData

    if ((!message && !imageData) || this.isTyping) {
      if (!message && !imageData) {
        alert('Vui lòng nhập tin nhắn hoặc tải lên hình ảnh')
      }
      return
    }

    // Create conversation if not exists
    if (!this.currentConversationId) {
      await this.startNewConversation()
    }

    this.addMessageToUI(message, imageData, "user")

    if (this.elements.chatInput) {
      this.elements.chatInput.value = ""
    }

    this.clearImagePreview()

    this.showTypingIndicator()

    try {
      // Send message to backend with RAG and CNN integration
      const response = await fetch('/api/chat/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          image: imageData,
          conversation_id: this.currentConversationId
        })
      })

      const data = await response.json()

      if (data.success) {
        this.hideTypingIndicator()

        // Hiển thị kết quả phân tích hình ảnh nếu có
        let responseContent = data.response
        if (data.cv_prediction) {
          responseContent = `
            <div class="cv-result">
              <div class="cv-prediction">
                <i class="fas fa-microscope me-2"></i>
                ${data.cv_prediction}
                ${data.confidence ? `<div class="disease-confidence">Độ tin cậy: ${(data.confidence * 100).toFixed(1)}%</div>` : ''}
              </div>
              <div class="rag-response">${data.response}</div>
            </div>
          `
        }

        this.addMessageToUI(responseContent, null, "bot")
        await this.loadConversations()
      } else {
        throw new Error(data.error || 'Failed to get response')
      }
    } catch (error) {
      this.hideTypingIndicator()
      const errorMsg = "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau."
      this.addMessageToUI(errorMsg, null, "bot")
      console.error("Chatbot error:", error)
    }
  }

  addMessageToUI(content, imageData, type) {
    const timestamp = new Date().toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    })

    this.renderMessage({
      content,
      imageData,
      type,
      timestamp,
    })

    this.scrollToBottom()
  }

  renderMessage(message) {
    if (!this.elements.chatMessages) return

    const messageElement = document.createElement("div")
    messageElement.className = `message ${message.type}`

    let messageHTML = ''
    if (message.type === "user") {
      messageHTML = `
        <div class="message-content">
          ${message.imageData ? `<img src="${message.imageData}" class="chat-image-preview" alt="Hình ảnh đã tải lên">` : ''}
          ${message.content ? `<p>${this.formatMessageContent(message.content)}</p>` : ''}
          <div class="message-time">${this.escapeHtml(message.timestamp)}</div>
        </div>
        <div class="message-avatar">
          <i class="fas fa-user"></i>
        </div>
      `
    } else {
      messageHTML = `
        <div class="message-avatar">
          <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
          ${this.formatMessageContent(message.content)}
          <div class="message-time">${this.escapeHtml(message.timestamp)}</div>
        </div>
      `
    }

    messageElement.innerHTML = messageHTML
    this.elements.chatMessages.appendChild(messageElement)
  }

  formatMessageContent(content) {
    if (!content) return ''

    // Xử lý markdown đơn giản và emoji
    return this.escapeHtml(content)
      .replace(/\n/g, "<br>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/`(.*?)`/g, "<code>$1</code>")
  }

  escapeHtml(unsafe) {
    if (!unsafe) return ''
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;")
  }

  showTypingIndicator() {
    if (!this.elements.chatMessages) return

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
    if (!this.elements.chatMessages) return

    setTimeout(() => {
      this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight
    }, 100)
  }

  async clearCurrentChat() {
    if (!confirm("Bạn có chắc muốn xóa cuộc trò chuyện hiện tại?")) return

    try {
      if (this.currentConversationId) {
        const response = await fetch(`${this.apiBaseUrl}/conversations/${this.currentConversationId}`, {
          method: "DELETE",
        })

        if (!response.ok) throw new Error("Failed to delete conversation")

        this.conversations = this.conversations.filter((c) => c.id !== this.currentConversationId)
      }

      if (this.elements.chatHistory) {
        this.renderConversationsSidebar(this.conversations)
      }

      await this.startNewConversation()
    } catch (error) {
      console.error("Error deleting conversation:", error)
      alert('Có lỗi xảy ra khi xóa cuộc trò chuyện')
    }
  }

  async clearAllHistory() {
    if (!confirm("Bạn có chắc muốn xóa tất cả lịch sử trò chuyện? Hành động này không thể hoàn tác.")) return

    try {
      // Delete all conversations
      const deletePromises = this.conversations.map(conv =>
        fetch(`${this.apiBaseUrl}/conversations/${conv.id}`, { method: "DELETE" })
      )

      await Promise.all(deletePromises)

      this.conversations = []

      if (this.elements.chatMessages) {
        this.elements.chatMessages.innerHTML = ""
      }

      if (this.elements.chatHistory) {
        this.renderConversationsSidebar([])
      }

      await this.startNewConversation()
    } catch (error) {
      console.error("Error clearing history:", error)
      alert('Có lỗi xảy ra khi xóa lịch sử')
    }
  }

  addWelcomeMessage() {
    if (!this.elements.chatMessages) return

    const welcomeMessage = `👋 **Xin chào! Tôi là chatbot tư vấn da liễu thông minh**

Tôi có thể giúp bạn với các vấn đề về:

🎯 **Phân tích hình ảnh** - Gửi ảnh để nhận chẩn đoán sơ bộ
💊 **Tư vấn điều trị** - Mụn, nám, viêm da, dị ứng
🌿 **Chăm sóc da** - Routine phù hợp với loại da
⚠️ **Xử lý khẩn cấp** - Dị ứng, kích ứng da
📋 **Kiến thức chuyên môn** - Dựa trên tài liệu y khoa

**Bạn có thể:**
- Gửi hình ảnh da để phân tích AI
- Mô tả triệu chứng để được tư vấn
- Hỏi về bất kỳ vấn đề da liễu nào

Hãy bắt đầu bằng cách gửi tin nhắn hoặc hình ảnh!`

    this.addMessageToUI(welcomeMessage, null, "bot")
  }

  toggleTheme() {
    this.theme = this.theme === "light" ? "dark" : "light"
    this.applyTheme()
    localStorage.setItem("chatbot-theme", this.theme)
  }

  applyTheme() {
    document.documentElement.setAttribute("data-theme", this.theme)
    const icon = this.elements.themeToggle?.querySelector("i")
    if (icon) {
      icon.className = this.theme === "light" ? "fas fa-moon" : "fas fa-sun"
    }
  }
}

// Khởi tạo chatbot khi trang tải xong
document.addEventListener("DOMContentLoaded", () => {
  // Đợi một chút để đảm bảo tất cả element đã sẵn sàng
  setTimeout(() => {
    try {
      window.chatbot = new Chatbot()
      console.log('Chatbot initialized successfully')
    } catch (error) {
      console.error('Failed to initialize chatbot:', error)
    }
  }, 100)
})