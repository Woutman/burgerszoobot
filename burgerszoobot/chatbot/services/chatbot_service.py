from .llm_interface import query_gpt


def handle_chatbot_interaction(chat_history: list[dict[str, str]]) -> str:
    response = query_gpt(chat_history)
    
    return response