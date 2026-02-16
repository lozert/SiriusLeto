from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.author_service import AuthorService
from app.services.organization_topic_service import OrganizationTopicService
from app.services.recommendation_service import RecommendationService


async def get_db_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db


def get_author_service() -> AuthorService:
    return AuthorService()


def get_recommendation_service() -> RecommendationService:
    return RecommendationService()


def get_organization_topic_service() -> OrganizationTopicService:
    return OrganizationTopicService()

