import os
import json
import redis
import numpy as np
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()


def get_redis_client():
    return redis.Redis(host='localhost', port=6379,
                       db=0, decode_responses=True)


class SemanticCache:
    """Cache semântico: busca respostas por similaridade de cosseno nos embeddings."""

    CACHE_PREFIX = "semantic_cache:"
    INDEX_KEY = "semantic_cache:index"

    def __init__(self, threshold: float = 0.85, ttl: int = 60):
        self.redis = get_redis_client()
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2",
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )
        self.threshold = threshold
        self.ttl = ttl

    def _cosine_similarity(self, a: list, b: list) -> float:
        a, b = np.array(a), np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def get(self, query: str) -> str | None:
        query_embedding = self.embeddings.embed_query(query)

        best_score = 0.0
        best_response = None

        for key in self.redis.smembers(self.INDEX_KEY):
            entry = self.redis.hgetall(key)
            if not entry:
                # Chave expirou, remove do índice
                self.redis.srem(self.INDEX_KEY, key)
                continue

            similarity = self._cosine_similarity(
                query_embedding, json.loads(entry["embedding"])
            )
            if similarity > best_score:
                best_score = similarity
                best_response = entry["response"]

        if best_score >= self.threshold:
            return best_response
        return None

    def set(self, query: str, response: str):
        query_embedding = self.embeddings.embed_query(query)
        key = f"{self.CACHE_PREFIX}{query}"

        self.redis.hset(key, mapping={
            "query": query,
            "embedding": json.dumps(query_embedding),
            "response": response,
        })
        self.redis.expire(key, self.ttl)
        self.redis.sadd(self.INDEX_KEY, key)
        # Mantém o índice vivo enquanto houver entradas
        self.redis.expire(self.INDEX_KEY, self.ttl * 10)
