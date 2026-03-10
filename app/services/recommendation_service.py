import asyncio
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models.organization import Organization
from app.db.models.organization_topic import OrganizationTopic
from app.db.models.publication import Publication
from app.db.models.topic import TopicDTO
from http_embedder import HttpEmbedder
from app.schemas.recommendation import (
    OrganizationRecommendation,
    OrganizationTopicAverageRecommendation,
)


class RecommendationService:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self._topic_milvus = None
        self._embedder = HttpEmbedder()

    def _get_topic_milvus(self):
        if self._topic_milvus is None:
            from app.clients.MilvusClient import Topic

            self._topic_milvus = Topic()
        return self._topic_milvus

    async def _get_query_embedding(self, query: str) -> list[float]:
        prefixed_query = query if query.startswith("query:") else f"query: {query}"
        embeddings = await asyncio.to_thread(self._embedder.embed, [prefixed_query])
        embedding = embeddings[0]
        self.logger.debug(
            "Got embedding of length %d from HTTP embedder",
            len(embedding),
        )
        return embedding

    async def _get_similar_topic_ids(
        self,
        embedding: list[float],
        top_topics: int,
    ) -> list[int]:
        try:
            search_result = await self._get_topic_milvus().search(
                embedding=embedding,
                top_k=top_topics,
                output_fields=["id"],
            )
        except Exception as exc:
            self.logger.error("Milvus search failed: %s", exc)
            return []

        topic_ids: list[int] = []
        if not search_result:
            return []

        hits = search_result[0]
        for hit in hits:
            topic_id = getattr(hit, "id", None)
            if topic_id is None and hasattr(hit, "entity"):
                try:
                    topic_id = hit.entity.get("id")
                except Exception:
                    topic_id = None

            if topic_id is not None:
                try:
                    topic_ids.append(int(topic_id))
                except (TypeError, ValueError):
                    continue

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

    async def _get_similar_topic_ids_from_db(
        self,
        db: AsyncSession,
        query: str,
        top_topics: int,
    ) -> list[int]:
        stmt = (
            select(TopicDTO.num)
            .where(TopicDTO.name.ilike(f"%{query}%"))
            .order_by(TopicDTO.prominence_percentile.desc())
            .limit(top_topics)
        )
        result = await db.execute(stmt)
        return [row.num for row in result.all()]

    async def recommend_organizations_by_topic(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10,
    ) -> List[OrganizationRecommendation]:
        self.logger.info("Recommend organizations for query=%r limit=%s", query, limit)

        topic_subq = (
            select(TopicDTO.num, TopicDTO.name)
            .where(TopicDTO.name.ilike(f"%{query}%"))
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
            .join(topic_subq, topic_subq.c.num == Publication.topic_id)
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
    ) -> List[OrganizationTopicAverageRecommendation]:
        self.logger.info(
            "Recommend organizations by organization_topic coefficients "
            "for query=%r limit=%s top_topics=%s",
            query,
            limit,
            10,
        )

        embedding = await self._get_query_embedding(query)
        topic_ids = await self._get_similar_topic_ids(embedding=embedding, top_topics=10)

        if not topic_ids:
            self.logger.info(
                "Falling back to DB topic search for query=%r because vector search returned no topics",
                query,
            )
            topic_ids = await self._get_similar_topic_ids_from_db(
                db=db,
                query=query,
                top_topics=10,
            )

        if not topic_ids:
            self.logger.debug("No topic ids found for query=%r", query)
            return []

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
            "Found %d rows for coefficient-based recommendations",
            len(rows),
        )

        return [
            OrganizationTopicAverageRecommendation(
                organization_id=row.organization_id,
                organization_name=row.organization_name,
                average_coefficient=float(row.avg_coefficient or 0.0),
            )
            for row in rows
        ]
