import json
from typing import Any, List

import requests

from settings import settings


class HttpEmbedder:
    def __init__(self, url: str | None = None, timeout: float = 150.0):
        self.url = url or settings.vectorize_url
        self.timeout = timeout

    def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            response = requests.post(
                self.url,
                json={"queries": texts},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"Embedding request failed: {exc}") from exc

        embeddings = self._extract_embeddings(payload)
        if not embeddings:
            raise RuntimeError("Embedding response did not contain any vectors")
        return embeddings

    def encode(
        self,
        texts: List[str],
        normalize_embeddings: bool = True,
        **_: object,
    ) -> List[List[float]]:
        embeddings = self.embed(texts)
        if normalize_embeddings:
            return [self._normalize(vector) for vector in embeddings]
        return embeddings

    @staticmethod
    def _normalize(vector: List[float]) -> List[float]:
        norm = sum(value * value for value in vector) ** 0.5
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def _extract_embeddings(self, payload: Any) -> List[List[float]]:
        if isinstance(payload, list) and len(payload) == 1 and isinstance(payload[0], str):
            payload = json.loads(payload[0])

        if self._is_embedding_matrix(payload):
            return payload

        if isinstance(payload, dict):
            for key in ("embeddings", "vectors", "data", "result", "items"):
                value = payload.get(key)
                if self._is_embedding_matrix(value):
                    return value
                if isinstance(value, list):
                    nested = self._extract_embeddings(value)
                    if nested:
                        return nested

        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    nested = self._extract_embeddings(item)
                    if nested:
                        return nested

        raise RuntimeError(f"Unexpected embedding response payload: {type(payload).__name__}")

    @staticmethod
    def _is_embedding_matrix(value: Any) -> bool:
        if not isinstance(value, list) or not value:
            return False
        return all(
            isinstance(vector, list)
            and all(isinstance(component, (int, float)) for component in vector)
            for vector in value
        )


if __name__ == "__main__":
    http_embedding = HttpEmbedder()
    text = "Математическое моделирование"
    embedding = http_embedding.embed([text])
    
    print(embedding)
    print(len(embedding[0]))
