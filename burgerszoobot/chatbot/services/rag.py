import os
import json
from dataclasses import dataclass
from typing import Optional

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.db.base import UniqueConstraintError
import torch
from transformers import AutoModel, AutoTokenizer
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


@dataclass
class RAGSettings:
    rag: bool
    classification: bool
    rephrasing: bool
    reranking: bool
    repacking: bool


class RAGPipeline:
    def __init__(self, settings: RAGSettings) -> None:
        self.settings = settings

    def retrieve_relevant_info(self, message_history: list[dict[str, str]]) -> Optional[str]:
        if self.settings.classification:
            if not self._is_rag_necessary(message_history=message_history):
                return
        
        if self.settings.rephrasing:
            query = self._rephrase_query(message_history=message_history)
        else:    
            query = message_history[-1]['content']

        results = self._retrieve_documents(query=query, top_n=20, min_score=0.6) # TODO: Include top_n and min_distance in settings

        if self.settings.reranking:
            results = self._rerank_documents(query=query, documents=results, top_n=5, min_score=0.0) # TODO: Include top_n in settings
        
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

        relevant_documents = self._filter_documents_by_distance(documents=documents, distances=distances, max_distance=min_score)

        return relevant_documents

    def _rerank_documents(self, query: str, documents: list[str], top_n: int, min_score: float) -> list[str]:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        tokenizer = AutoTokenizer.from_pretrained('ce-esci-MiniLM-L12-v2', model_type='flashrank')
        model = AutoModel.from_pretrained('ce-esci-MiniLM-L12-v2', model_type='flashrank')
        model.to(device)
        model.eval()

        query_input = tokenizer(query, return_tensors='pt', padding=True, truncation=True, max_length=None)
        query_input = {k: v.to(device) for k, v in query_input.items()}
        
        scores = []
        for doc in documents:
            doc_input = tokenizer(query, doc, return_tensors='pt', padding=True, truncation=True, max_length=None)
            doc_input = {k: v.to(device) for k, v in doc_input.items()}
            with torch.no_grad():
                outputs = model(**doc_input)
                score = outputs.logits
                scores.append(score.item())

        ranked_documents = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)

        # TODO: Function isn't finished
        
        return [doc for doc, score in ranked_documents[:top_n]]
    
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

    def _filter_documents_by_distance(self, documents: list[str], distances: list[float], max_distance: float) -> list[str]:
        indices_below_max_distance = [distances.index(distance) for distance in distances if distance <= max_distance]
        relevant_documents = [doc for doc in documents if documents.index(doc) in indices_below_max_distance]

        return relevant_documents
