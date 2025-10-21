import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app import app


class RAGSystem:
    #Constructor
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="dangvantuan/vietnamese-embedding"
        )
        # Kết nối Qdrant
        self.docsearch = QdrantVectorStore.from_existing_collection(
            embedding=self.embeddings,
            url=app.config['QDRANT_URL'],
            api_key=app.config['QDRANT_API_KEY'],
            collection_name=app.config['COLLECTION_NAME'],
        )
        #Retriever
        self.retriever = self.docsearch.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 40}
        )
        # LLM
        self.llm = ChatOpenAI(
            model=app.config['MODEL_LLM_NAME'],
            openai_api_key=app.config['OPENAI_API_KEY'],
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.4,
            max_tokens=2048
        )
        # Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key='answer'
        )
        self.system_prompt = (
            "Bạn là một trợ lý ảo chuyên về lĩnh vực y tế và sức khỏe da liễu. "
            "Hãy trả lời câu hỏi của người dùng dựa trên thông tin được cung cấp.\n\n"
            "Thông tin tham khảo:\n{context}\n\n"
            "Lịch sử hội thoại:\n{chat_history}\n\n"
            "Câu hỏi: {input}\n\n"
            "Hướng dẫn:\n"
            "- Trả lời bằng tiếng Việt tự nhiên, dễ hiểu\n"
            "- Tập trung vào thông tin từ tài liệu tham khảo\n"
            "- Giới hạn trong 3-4 câu\n"
            "- Nếu không có thông tin, hãy nói 'Xin lỗi, tôi không có đủ thông tin về vấn đề này.'"
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])


#GET RESPONSE
    def get_rag_response(self, query):
        try:
            # Tạo chain đơn giản
            question_answer_chain = create_stuff_documents_chain(
                self.llm,
                self.prompt
            )

            rag_chain = create_retrieval_chain(
                self.retriever,
                question_answer_chain
            )
            # Get response
            inputs = {
                "input": query,
                "chat_history": self.memory.chat_memory.messages
            }
            response = rag_chain.invoke(inputs)
            answer = response.get('answer', 'Xin lỗi, tôi không thể trả lời câu hỏi này.')
            # Save to memory
            self.memory.save_context({"input": query}, {"answer": answer})
            return answer

        except Exception as e:
            app.logger.error(f"RAG Error: {e}")
            return "Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi của bạn."

rag_chatbot = RAGSystem()