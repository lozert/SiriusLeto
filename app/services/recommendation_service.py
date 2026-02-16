from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models.organization import Organization
from app.db.models.publication import Publication
from app.db.models.topic import Topic
from app.schemas.recommendation import OrganizationRecommendation


class RecommendationService:
    """
    Сервис рекомендаций университетов (organization)
    по количеству публикаций в теме, близкой к запросу пользователя.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

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

