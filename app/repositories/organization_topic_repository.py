from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.organization_topic import OrganizationTopic


class OrganizationTopicRepository:
    """
    Репозиторий для работы с таблицей organization_topic.
    """

    async def get(self, db: AsyncSession, organization_id: int, topic_num: int) -> OrganizationTopic | None:
        stmt = select(OrganizationTopic).where(
            OrganizationTopic.organization_id == organization_id,
            OrganizationTopic.topic_num == topic_num,
        )
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def upsert(
        self,
        db: AsyncSession,
        organization_id: int,
        topic_num: int,
        coefficient: float,
    ) -> OrganizationTopic:
        obj = await self.get(db, organization_id=organization_id, topic_num=topic_num)
        if obj is None:
            obj = OrganizationTopic(
                organization_id=organization_id,
                topic_num=topic_num,
                coefficient=coefficient,
            )
            db.add(obj)
        else:
            obj.coefficient = coefficient

        await db.commit()
        await db.refresh(obj)
        return obj


organization_topic_repository = OrganizationTopicRepository()

