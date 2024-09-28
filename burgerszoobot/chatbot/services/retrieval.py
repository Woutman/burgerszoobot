import os

from dotenv import load_dotenv
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.api.types import Metadata
from chromadb.db.base import UniqueConstraintError

client = chromadb.PersistentClient(path=".")

load_dotenv("api_keys.env")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_embedding_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small"
)

try:
    collection = client.create_collection(name="zoo_documents", embedding_function=openai_embedding_function)
except UniqueConstraintError:
    collection = client.get_collection(name="zoo_documents", embedding_function=openai_embedding_function)


def ingest_document(document_id: str, document_text: str, metadata: Metadata = None) -> None:
    print(f"ingesting document {document_id}.")
    collection.add(
        ids=[document_id],
        documents=[document_text],
        metadatas=[metadata]
    )


def delete_document(document_id: str) -> None:
    collection.delete(ids=[document_id])


def retrieve_documents(query_texts: list[str], n_results: int) -> tuple[list[str], list[Metadata]]:
    results = collection.query(query_texts=query_texts, n_results=n_results)

    documents = [result['documents'] for result in results['results']]
    metadatas = [result['metadatas'] for result in results['results']]

    return documents, metadatas
