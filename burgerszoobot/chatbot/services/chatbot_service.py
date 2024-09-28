from .llm_interface import query_gpt
from .retrieval import retrieve_documents


def handle_chatbot_interaction(chat_history: list[dict[str, str]]) -> str:
    user_input = chat_history[-1]["content"]

    docs = retrieve_documents(query_text=user_input)

    # Write prompt to base answer only on retrieved documents

    response = query_gpt(chat_history=chat_history)
    
    return response