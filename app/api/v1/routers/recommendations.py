from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, get_recommendation_service
from app.schemas.recommendation import OrganizationRecommendation
from app.services.recommendation_service import RecommendationService


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/universities", response_model=List[OrganizationRecommendation])
async def recommend_universities(
    query: str = Query(..., description="Куда пользователь хочет поступать / какая область интересует"),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    service: RecommendationService = Depends(get_recommendation_service),
):
    """
    Возвращает список университетов (organization),
    отсортированный по количеству публикаций в темах,
    подходящих под текстовый запрос пользователя.
    """
    return await service.recommend_organizations_by_topic(db=db, query=query, limit=limit)

