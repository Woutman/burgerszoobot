from .llm_interface import query_gpt
from .rag import RAGSettings, RAGPipeline


def handle_chatbot_interaction(chat_history: list[dict[str, str]], rag_settings: RAGSettings) -> str:
    rag_pipeline = RAGPipeline(settings=rag_settings)
    response = rag_pipeline.retrieve_relevant_info(message_history=chat_history)
    
    if response:
        return response

    response = query_gpt(messages=chat_history)
    
    return response
