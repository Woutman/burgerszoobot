from .llm_interface import query_gpt
from .retrieval import retrieve_documents, retrieve_documents_with_example_answer, retrieve_documents_with_subqueries


def handle_chatbot_interaction(chat_history: list[dict[str, str]], retrieval_method: str) -> str:
    user_input = chat_history[-1]["content"]
    n_results = 5
    max_distance = 0.8

    match retrieval_method:
        case "basic":
            docs = retrieve_documents(query_text=user_input, n_results=n_results, max_distance=max_distance)
        case "augmented_query":
            docs = retrieve_documents_with_example_answer(query_text=user_input, n_results=n_results, max_distance=max_distance)
        case "subqueries":
            docs = retrieve_documents_with_subqueries(query_text=user_input, n_results=n_results, max_distance=max_distance)
    
    docs_unpacked = "\n\n".join(docs)

    prompt = f"Question: {user_input}.\nInformation: {docs_unpacked}"
    chat_history[-1]["content"] = prompt

    response = query_gpt(messages=chat_history)
    
    return response
