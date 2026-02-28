from typing import List

import asyncio
import requests
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from MilvusClient import TopicName
from app.core.logging import get_logger
from app.db.models.organization import Organization
from app.db.models.publication import Publication
from app.db.models.organization_topic import OrganizationTopic
from app.db.models.topic import Topic
from app.schemas.recommendation import (
    OrganizationRecommendation,
    OrganizationTopicAverageRecommendation,
)
from settings import settings


class RecommendationService:
    """
    Сервис рекомендаций университетов (organization)
    по количеству публикаций в теме, близкой к запросу пользователя.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        # Клиент Milvus для коллекции с эмбеддингами топиков
        self._topic_milvus = TopicName()

    async def _get_query_embedding(self, query: str) -> list[float]:
        """
        Получение эмбеддинга текста запроса через TorchServe (e5).

        Формат запроса к TorchServe может отличаться в вашей конфигурации.
        При необходимости скорректируйте тело запроса и парсинг ответа.
        """
        url = settings.torch_serve_url
        self.logger.debug("Request embedding from TorchServe url=%s", url)

        def _request_sync() -> list[float]:
            # По умолчанию отправляем JSON {"text": "..."}.
            # Если у вас другой формат (например {"inputs": "..."} или просто текст),
            # поменяйте это место.
            response = requests.post(url, json={"text": query}, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Ожидаем либо { "embedding": [...] }, либо просто список чисел.
            if isinstance(data, dict) and "embedding" in data:
                return list(map(float, data["embedding"]))
            if isinstance(data, list):
                return list(map(float, data))

            raise ValueError(f"Неожиданный формат ответа TorchServe: {data!r}")

        embedding = await asyncio.to_thread(_request_sync)
        self.logger.debug("Got embedding of length %d from TorchServe", len(embedding))
        return embedding

    async def _get_similar_topic_ids(
        self,
        embedding: list[float],
        top_topics: int,
    ) -> list[int]:
        """
        Векторный поиск топиков в Milvus по эмбеддингу запроса.

        Ожидается, что primary key коллекции Milvus совпадает с Topic.num.
        """
        try:
            search_result = await self._topic_milvus.search(
                embedding=embedding,
                top_k=top_topics,
                output_fields=["id"],
            )
        except Exception as exc:
            self.logger.error("Milvus search failed: %s", exc)
            return []

        topic_ids: list[int] = []

        # search_result — список Hits для каждого векторного запроса.
        # Мы ищем только по одному запросу, поэтому берём первый элемент.
        if not search_result:
            return []

        hits = search_result[0]
        for hit in hits:
            # PyMilvus обычно предоставляет id через hit.id,
            # но на всякий случай пробуем достать и из entity.
            topic_id = getattr(hit, "id", None)
            if topic_id is None and hasattr(hit, "entity"):
                try:
                    topic_id = hit.entity.get("id")
                except Exception:  # pragma: no cover - защита от неожиданных форматов
                    topic_id = None

            if topic_id is not None:
                try:
                    topic_ids.append(int(topic_id))
                except (TypeError, ValueError):
                    continue

        # Убираем дубликаты, сохраняя порядок.
        seen: set[int] = set()
        unique_topic_ids: list[int] = []
        for topic_id in topic_ids:
            if topic_id not in seen:
                seen.add(topic_id)
                unique_topic_ids.append(topic_id)

        self.logger.debug(
            "Milvus returned %d unique topic ids: %s",
            len(unique_topic_ids),
            unique_topic_ids,
        )
        return unique_topic_ids

    async def recommend_organizations_by_topic(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10,
    ) -> List[OrganizationRecommendation]:
        self.logger.info("Recommend organizations for query=%r limit=%s", query, limit)

        # Ищем темы, похожие на текст запроса пользователя
        topic_subq = (
            select(Topic.id, Topic.name)
            .where(Topic.name.ilike(f"%{query}%"))
            .subquery()
        )

        stmt = (
            select(
                Organization.id.label("organization_id"),
                Organization.name.label("organization_name"),
                topic_subq.c.name.label("topic_name"),
                func.count(Publication.id).label("publication_count"),
            )
            .join(Publication, Publication.organization_id == Organization.id)
            .join(topic_subq, topic_subq.c.id == Publication.topic_id)
            .group_by(Organization.id, Organization.name, topic_subq.c.name)
            .order_by(func.count(Publication.id).desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        self.logger.debug("Found %d rows for recommendations", len(rows))

        return [
            OrganizationRecommendation(
                organization_id=row.organization_id,
                organization_name=row.organization_name,
                topic=row.topic_name,
                publication_count=row.publication_count,
            )
            for row in rows
        ]

    async def recommend_organizations_by_topic_coefficients(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10,
        top_topics: int = 10,
    ) -> List[OrganizationTopicAverageRecommendation]:
        """
        Пайплайн с векторным поиском:
        1. Векторизуем текст запроса пользователя через TorchServe (e5).
        2. Ищем top_topics ближайших топиков в Milvus по эмбеддингам их названий.
        3. Находим все университеты, у которых есть эти топики в organization_topic.
        4. Для каждого университета считаем средний coefficient по найденным топикам.
        5. Возвращаем top-N университетов по среднему коэффициенту.
        """
        self.logger.info(
            "Recommend organizations by organization_topic coefficients "
            "for query=%r limit=%s top_topics=%s",
            query,
            limit,
            top_topics,
        )

        # 1–2. Векторизуем запрос и находим ближайшие топики в Milvus
        embedding = await self._get_query_embedding(query)
        topic_ids = await self._get_similar_topic_ids(embedding=embedding, top_topics=top_topics)

        if not topic_ids:
            self.logger.debug("No topic ids found for query=%r", query)
            return []

        # 3–4. Средний coefficient по выбранным топикам для каждого университета
        stmt = (
            select(
                Organization.id.label("organization_id"),
                Organization.name.label("organization_name"),
                func.avg(OrganizationTopic.coefficient).label("avg_coefficient"),
            )
            .join(OrganizationTopic, OrganizationTopic.organization_id == Organization.id)
            .where(OrganizationTopic.topic_num.in_(topic_ids))
            .group_by(Organization.id, Organization.name)
            .order_by(func.avg(OrganizationTopic.coefficient).desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        self.logger.debug(
            "Found %d rows for coefficient-based recommendations", len(rows)
        )

        return [
            OrganizationTopicAverageRecommendation(
                organization_id=row.organization_id,
                organization_name=row.organization_name,
                average_coefficient=float(row.avg_coefficient or 0.0),
            )
            for row in rows
        ]


