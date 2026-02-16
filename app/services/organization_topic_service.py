from typing import List, Protocol, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models.author import Author
from app.db.models.publication import Publication
from app.db.models.publication_author import PublicationAuthor
from app.db.models.organization_topic import OrganizationTopic
from app.repositories.organization_topic_repository import organization_topic_repository


class CoefficientStrategy(Protocol):
    """
    Стратегия вычисления коэффициента для пары (organization, topic).
    Позволяет легко заменить алгоритм в одном месте.
    """

    async def calculate(self, db: AsyncSession, organization_id: int, topic_num: int) -> float: ...


class PublicationCountCoefficientStrategy:
    """
    Базовый алгоритм:
    коэффициент = среднее значение метрики публикаций
    данной организации в данном топике.

    Сейчас в качестве метрики используется `citations_num`.
    При желании можно заменить на другую колонку (например, views_num).
    """

    async def calculate(self, db: AsyncSession, organization_id: int, topic_num: int) -> float:
        # Среднее citations_num по всем публикациям организации в данном топике.
        stmt = (
            select(func.avg(Publication.citations_num))
            .join(PublicationAuthor, PublicationAuthor.publication_id == Publication.id)
            .join(Author, Author.id == PublicationAuthor.author_id)
            .where(
                Author.organization_id == organization_id,
                Publication.topic_num == topic_num,
                Publication.citations_num.isnot(None),
            )
        )
        result = await db.execute(stmt)
        avg_value = result.scalar()

        return float(avg_value or 0.0)


class OrganizationTopicService:
    """
    Сервис для пересчёта коэффициентов в organization_topic.
    Логику можно менять через подстановку другой CoefficientStrategy.
    """

    def __init__(self, strategy: CoefficientStrategy | None = None):
        self.strategy: CoefficientStrategy = strategy or PublicationCountCoefficientStrategy()
        self.repo = organization_topic_repository
        self.logger = get_logger(self.__class__.__name__)

    async def recalculate_for_pair(
        self,
        db: AsyncSession,
        organization_id: int,
        topic_num: int,
        ) -> OrganizationTopic:
        self.logger.info(
            "Recalculating coefficient for organization_id=%s, topic_num=%s",
            organization_id,
            topic_num,
        )
        coefficient = await self.strategy.calculate(db, organization_id=organization_id, topic_num=topic_num)
        return await self.repo.upsert(
            db,
            organization_id=organization_id,
            topic_num=topic_num,
            coefficient=coefficient,
        )

    async def recalculate_all(self, db: AsyncSession) -> List[OrganizationTopic]:
        """
        Оптимизированный пересчёт коэффициентов для всех пар (organization_id, topic_num).

        Логика:
        1. Берём публикации по topic_num.
        2. Через авторов определяем организации.
        3. Для каждой пары (organization_id, topic_num) считаем:
           коэффициент = среднее citations_num по всем публикациям организации в этом topic.

        На SQL это один агрегирующий запрос с GROUP BY.
        """
        stmt = (
            select(
                Author.organization_id.label("organization_id"),
                Publication.topic_num.label("topic_num"),
                func.avg(Publication.citations_num).label("avg_citations"),
            )
            .join(PublicationAuthor, PublicationAuthor.author_id == Author.id)
            .join(Publication, Publication.id == PublicationAuthor.publication_id)
            .where(
                Author.organization_id.isnot(None),
                Publication.topic_num.isnot(None),
                Publication.citations_num.isnot(None),
            )
            .group_by(Author.organization_id, Publication.topic_num)
            .order_by(Publication.topic_num, Author.organization_id)
        )

        rows_result = await db.execute(stmt)
        rows = rows_result.all()

        self.logger.info(
            "Found %d (organization, topic_num) groups to recalculate",
            len(rows),
        )

        results: List[OrganizationTopic] = []
        for row in rows:
            organization_id = row.organization_id
            topic_num = row.topic_num
            coefficient = float(row.avg_citations or 0.0)

            results.append(
                await self.repo.upsert(
                    db=db,
                    organization_id=organization_id,
                    topic_num=topic_num,
                    coefficient=coefficient,
                )
            )

        return results

