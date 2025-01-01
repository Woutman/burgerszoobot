import os
import json
from dataclasses import dataclass
from typing import Optional

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.db.base import UniqueConstraintError
from chromadb.api.types import Metadata
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv

from .llm_instructions import INSTRUCTIONS_CLASSIFICATION, INSTRUCTIONS_REPHRASING, INSTRUCTIONS_SUMMARIZATION
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


@dataclass
class RAGSettings:
    rag: bool
    retrieval_top_n: int
    classification: bool
    rephrasing: bool
    reranking: bool
    reranking_top_n: int
    repacking: bool


class RAGPipeline:
    def __init__(self, settings: RAGSettings) -> None:
        self.settings = settings

    def retrieve_relevant_info(self, message_history: list[dict[str, str]]) -> Optional[str]:
        if self.settings.rephrasing:
            query = self._rephrase_query(message_history=message_history)
            message_history[-1]['content'] = query
        else:    
            query = message_history[-1]['content']

        if self.settings.classification:
            if not self._is_rag_necessary(message_history=message_history):
                return

        results = self._retrieve_documents(query=query, top_n=self.settings.retrieval_top_n, min_score=0.0)

        if self.settings.reranking:
            results = self._rerank_documents(query=query, documents=results, top_n=self.settings.reranking_top_n, min_score=0.0)
        
        if self.settings.repacking:
            results = self._reverse_documents(documents=results)

        response = self._summarize_documents(query=query, documents=results)
        
        return response
            
    def _is_rag_necessary(self, message_history: list[dict[str, str]]) -> bool:
        messages = [
            {"role": "system", "content": INSTRUCTIONS_CLASSIFICATION},
            {"role": "user", "content": json.dumps(message_history)}
        ]

        result = query_gpt(messages=messages, temperature=0.0)

        if result == "YES":
            return True
        elif result == "NO":
            return False
        else:
            raise ValueError("Classification step of RAG pipeline returned something other than 'YES' or 'NO'.")
        
    def _rephrase_query(self, message_history: list[dict[str, str]]) -> str:
        messages = [
            {"role": "system", "content": INSTRUCTIONS_REPHRASING},
            {"role": "user", "content": json.dumps(message_history)}
        ]

        result = query_gpt(messages=messages, temperature=0.0)

        return result
    
    def _retrieve_documents(self, query: str, top_n: int, min_score: float) -> list[str]:
        results = collection.query(query_texts=query, n_results=top_n)
        if not (documents := results['documents']) or not (distances := results['distances']):
            return []

        documents = documents[0]
        distances = distances[0]

        relevant_documents = self._filter_documents_by_distance(documents=documents, distances=distances, min_distance=min_score)

        return relevant_documents

    def _rerank_documents(self, query: str, documents: list[str], top_n: int, min_score: float) -> list[str]:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        model_name_or_path = "Alibaba-NLP/gte-multilingual-reranker-base"

        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name_or_path,
            revision="815b4a86b71f0ecba053e5814a6c24aa7199301e", 
            trust_remote_code=True,
            torch_dtype=torch.float16
        )
        model.to(device)
        model.eval()

        pairs = [[query, doc] for doc in documents]
        with torch.no_grad():
            inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
            inputs = {key: value.to(device) for key, value in inputs.items()}
            scores = model(**inputs, return_dict=True).logits.view(-1, ).float()

        ranked_documents = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        
        return [doc for doc, scores in ranked_documents[:top_n]]
    
    def _reverse_documents(self, documents: list[str]) -> list[str]:
        documents.reverse()
        return documents

    def _summarize_documents(self, query: str, documents: list[str]) -> str:
        documents_as_str = "\n\n".join(documents)
        messages = [
            {"role": "system", "content": INSTRUCTIONS_SUMMARIZATION},
            {"role": "user", "content": f"Documents:\n{documents_as_str}\n\nQuery: {query}"}
        ]

        result = query_gpt(messages=messages, temperature=0.0)

        return result

    def _filter_documents_by_distance(self, documents: list[str], distances: list[float], min_distance: float) -> list[str]:
        indices_above_min_distance = [distances.index(distance) for distance in distances if distance >= min_distance]
        relevant_documents = [doc for doc in documents if documents.index(doc) in indices_above_min_distance]

        return relevant_documents
