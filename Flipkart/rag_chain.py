from langchain_groq import ChatGroq
from langchain.chians import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessagesHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from Flipkart.config import Config

class RAGCainBuilder:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.chat_model = ChatGroq(model=Config.RAG_MODEL, temperature=0.5)
        self.history_store = {}

    def get_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.history_store:
            self.history_store[session_id] = ChatMessageHistory
        return self.history_store[session_id]
    
    def build_chain(self):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        context_prompt = ChatPromptTemplate.from_messages([
            ("system", 
            "You are a helpful assistant reviewing customer feedback for Flipkart products. "
            "Based on the provided context, identify useful patterns, product strengths, or weaknesses. "
            "Your goal is to help users make informed purchase decisions."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")])

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system",
            "You are an e-commerce assistant that answers customer questions based on product reviews and titles. "
            "Only use the information in the context below. Be accurate, concise, and helpful. "
            "CONTEXT:\n{context}\n\n"
            "QUESTION: {input}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")])


        history_aware_retriever = create_history_aware_retriever(self.model, retriever, context_prompt)
        question_ansewer_chain = create_stuff_documents_chain(self.model, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_ansewer_chain)
        return RunnableWithMessagesHistory(
            rag_chain,
            self.get_history,
            input_message_key="input",
            history_message_key="chat_history",
            output_message_key="answer"
        )

         
      
   