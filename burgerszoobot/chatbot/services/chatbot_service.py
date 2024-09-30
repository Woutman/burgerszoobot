from .llm_interface import query_gpt
from .retrieval import retrieve_documents


def handle_chatbot_interaction(chat_history: list[dict[str, str]]) -> str:
    user_input = chat_history[-1]["content"]

    docs = retrieve_documents(query_texts=[user_input], n_results=5)
    docs_unpacked = "\n\n".join(docs)

    prompt = f"Question: {user_input}.\nInformation: {docs_unpacked}"
    chat_history[-1]["content"] = prompt

    response = query_gpt(chat_history=chat_history)
    
    return response
