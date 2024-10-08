import os

from dotenv import load_dotenv
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.api.types import Metadata
from chromadb.db.base import UniqueConstraintError

from .llm_instructions import INSTRUCTIONS_RETRIEVAL_WITH_EXAMPLE_ANSWER, INSTRUCTIONS_RETRIEVAL_WITH_SUBQUESTIONS
from .llm_interface import query_gpt


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path_to_chromadb = os.path.join(BASE_DIR, 'chromadb')
client = chromadb.PersistentClient(path=path_to_chromadb)

load_dotenv("api_keys.env")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_embedding_function = embedding_functions.OpenAIEmbeddingFunction( # type: ignore
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small"
)

try:
    collection = client.create_collection(name="zoo_documents", embedding_function=openai_embedding_function)
except UniqueConstraintError:
    collection = client.get_collection(name="zoo_documents", embedding_function=openai_embedding_function)


def ingest_document(document_id: str, document_text: str, metadata: Metadata | None = None) -> None:
    print(f"ingesting document {document_id}.")
    collection.add(
        ids=[document_id],
        documents=[document_text],
        metadatas=[metadata] if metadata else None
    )


def delete_document(document_id: str) -> None:
    collection.delete(ids=[document_id])


def retrieve_documents(query_text: str, n_results: int, max_distance: float) -> list[str]:
    '''
    Basic retrieval function.
    '''
    results = collection.query(query_texts=query_text, n_results=n_results)
    if not (documents := results['documents']) or not (distances := results['distances']):
        return []

    documents = documents[0]
    distances = distances[0]

    relevant_documents = _filter_documents_by_distance(documents=documents, distances=distances, max_distance=max_distance)

    return relevant_documents


def retrieve_documents_with_example_answer(query_text: str, n_results: int, max_distance: float) -> list[str]:
    '''
    Retrieves documents based on user query, combined with an example answer generated by an LLM. 
    This answer doesn't need to be factually correct, but its structure and contents can assist with retrieval of documents.
    '''
    augmented_query = _augment_query_with_example_answer(query_text=query_text)
    
    results = collection.query(query_texts=augmented_query, n_results=n_results)
    if not (documents := results['documents']) or not (distances := results['distances']):
        return []

    documents = documents[0]
    distances = distances[0]

    relevant_documents = _filter_documents_by_distance(documents=documents, distances=distances, max_distance=max_distance)

    return relevant_documents


def _augment_query_with_example_answer(query_text: str) -> str:
    messages = [
        {"role": "system", "content": INSTRUCTIONS_RETRIEVAL_WITH_EXAMPLE_ANSWER},
        {"role": "user", "content": query_text}
    ]

    hypothetical_answer = query_gpt(messages=messages)

    joint_query = f"{query_text} {hypothetical_answer}"

    return joint_query


def retrieve_documents_with_subqueries(query_text: str, n_results: int, max_distance: float) -> list[str]:
    '''
    Retrieves documents based on user query, combined with subqueries generated by an LLM that each answer a specific part of the main query. 
    '''
    subqueries = _augment_query_with_subquestions(query_text=query_text)
    queries = [query_text] + subqueries

    results = collection.query(query_texts=queries, n_results=n_results)

    documents_of_all_queries = results['documents']
    distances_of_all_queries = results['distances']
    if not documents_of_all_queries or not distances_of_all_queries:
        return []

    relevant_docs_all_queries = list()
    for documents_of_query, distances_of_query in zip(documents_of_all_queries, distances_of_all_queries):
        relevant_docs_of_query = _filter_documents_by_distance(documents=documents_of_query, distances=distances_of_query, max_distance=max_distance)
        relevant_docs_all_queries.extend(relevant_docs_of_query)

    return relevant_docs_all_queries


def _augment_query_with_subquestions(query_text: str) -> list[str]:
    messages = [
        {"role": "system", "content": INSTRUCTIONS_RETRIEVAL_WITH_SUBQUESTIONS},
        {"role": "user", "content": query_text}
    ]

    response = query_gpt(messages=messages)

    subqueries = response.split("\n")

    return subqueries


def _filter_documents_by_distance(documents: list[str], distances: list[float], max_distance: float) -> list[str]:
    indices_below_max_distance = [distances.index(distance) for distance in distances if distance <= max_distance]
    relevant_documents = [doc for doc in documents if documents.index(doc) in indices_below_max_distance]

    return relevant_documents
