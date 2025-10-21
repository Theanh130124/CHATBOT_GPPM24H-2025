import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from app import app


class RAGSystem:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="dangvantuan/vietnamese-embedding"
        )
        self.docsearch = QdrantVectorStore.from_existing_collection(
            embedding=self.embeddings,
            url=app.config['QDRANT_URL'],
            api_key=app.config['QDRANT_API_KEY'],
            collection_name=app.config['COLLECTION_NAME'],
        )
        self.retriever = self.docsearch.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 40}
        )
        self.llm = ChatOpenAI(
            model=app.config['MODEL_LLM_NAME'],
            openai_api_key=app.config['OPENAI_API_KEY'],
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.4,
            max_tokens=2048
        )

        self.system_prompt = (
            "Bạn là trợ lý ảo chuyên về y tế da liễu.\n"
            "Thông tin tham khảo:\n{context}\n\n"
            "Lịch sử hội thoại:\n"
            "Câu hỏi: {input}\n\n"
            "- Trả lời bằng tiếng Việt dễ hiểu\n"
            "- Dựa trên tài liệu tham khảo\n"
            "- Giới hạn 3-4 câu\n"
            "- Nếu không có thông tin, nói 'Xin lỗi, tôi không có đủ thông tin về vấn đề này.'"
        )

        # Prompt template không sử dụng memory trong system prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

    def _get_conversation_messages(self, conversation_id):
        """
        Lấy lịch sử hội thoại và chuyển đổi sang định dạng LangChain messages
        """
        from app.models import ChatMessage

        messages = ChatMessage.query.filter_by(
            conversation_id=conversation_id
        ).order_by(ChatMessage.timestamp.asc()).all()

        # Chuyển đổi sang định dạng LangChain messages
        langchain_messages = []
        for msg in messages:
            if msg.message_type == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.message_type == "bot":
                langchain_messages.append(AIMessage(content=msg.content))

        return langchain_messages

    def get_rag_response(self, query, conversation_id):
        """
        Lấy response từ RAG cho 1 conversation_id
        """
        try:
            # 1. Lấy lịch sử chat từ DB cho conversation
            chat_history = self._get_conversation_messages(conversation_id)

            # 2. Tạo memory đúng cách - KHÔNG truyền chat_history vào constructor
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )

            # 3. Thêm tin nhắn vào memory thủ công
            for message in chat_history:
                if isinstance(message, HumanMessage):
                    memory.chat_memory.add_user_message(message.content)
                elif isinstance(message, AIMessage):
                    memory.chat_memory.add_ai_message(message.content)

            # 4. Tạo chain
            question_answer_chain = create_stuff_documents_chain(
                self.llm,
                self.prompt
            )
            rag_chain = create_retrieval_chain(
                self.retriever,
                question_answer_chain
            )

            # 5. Tạo input với chat_history từ memory
            inputs = {
                "input": query,
                "chat_history": memory.chat_memory.messages
            }

            # 6. Lấy response
            response = rag_chain.invoke(inputs)
            answer = response.get('answer', 'Xin lỗi, tôi không thể trả lời câu hỏi này.')

            return answer

        except Exception as e:
            app.logger.error(f"RAG System Error: {e}")
            return "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại."


rag_chatbot = RAGSystem()