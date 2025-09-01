from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq

from Ecommerce_agent.config import Config


class RAGChainBuilder:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.model = ChatGroq(model=Config.RAG_MODEL, temperature=0.5)
        self.history_store = {}

    def _get_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.history_store:
            self.history_store[session_id] = ChatMessageHistory()
        return self.history_store[session_id]

    def build_chain(self):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        # Prompt to reformulate follow-ups as standalone questions
        context_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "Given the chat history and user message, rewrite it as a standalone "
                        "question."
                    ),
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        # Advanced QA prompt with formatting and user-oriented tone
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are a helpful and professional assistant specialized in e-commerce "
                        "product recommendations.\n\n"
                        "Only use the information provided in the context (product titles and "
                        "structured details).\n"
                        "**Do not quote or mention customer reviews or feedback explicitly**.\n"
                        "Your role is to give direct, concise, and fact-based responses, in a "
                        "clear and friendly tone.\n\n"
                        "Instructions:\n"
                        '- Avoid saying "users said", "reviewers mentioned", or using quotes.\n'
                        "- Never invent information. If something is not in the context, say so "
                        "politely.\n"
                        "- If multiple products are mentioned, format your answer like this:\n\n"
                        "Example:\n"
                        "Here are some options:\n\n"
                        "• **Product 1**  \n"
                        "  Short description of product 1.\n\n"
                        "• **Product 2**  \n"
                        "  Short description of product 2.\n\n"
                        "• **Product 3**  \n"
                        "  Short description of product 3.\n\n"
                        "- Always use:\n"
                        "  • Bullet points (`•`)\n"
                        "  • Line breaks (`\\n`)\n"
                        "  • Bold titles\n"
                        "  • Friendly closing question at the end\n\n"
                        "Context:\n"
                        "{context}\n\n"
                        "Now answer the user's question using only the above context.\n"
                    ),
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            self.model, retriever, context_prompt
        )

        question_answer_chain = create_stuff_documents_chain(self.model, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        return RunnableWithMessageHistory(
            rag_chain,
            self._get_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
