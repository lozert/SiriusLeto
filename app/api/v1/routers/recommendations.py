from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, get_recommendation_service
from app.schemas.recommendation import OrganizationTopicAverageRecommendation
from app.services.recommendation_service import RecommendationService

# Лимит результатов: не более 50
MAX_RESULTS_LIMIT = 50

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get(
    "/universities-by-coefficients",
    response_model=List[OrganizationTopicAverageRecommendation],
)
async def recommend_universities_by_coefficients(
    query: str = Query(
        ...,
        description=(
            "Куда пользователь хочет поступать / какая область интересует. "
            "Используется для векторного поиска релевантных топиков."
        ),
    ),
    limit: int = Query(10, ge=1, le=MAX_RESULTS_LIMIT, description="Сколько университетов вернуть (макс. 50)"),
    top_topics: int = Query(
        10,
        ge=1,
        le=100,
        description="Сколько ближайших топиков учитывать при расчёте среднего коэффициента",
    ),
    db: AsyncSession = Depends(get_db_session),
    service: RecommendationService = Depends(get_recommendation_service),
):
    """
    Векторный поиск: рекомендации университетов по organization_topic.
    1. Векторизуем запрос (TorchServe), ищем ближайшие топики в Milvus.
    2. Берём коэффициенты для найденных топиков и университетов.
    3. Средний коэффициент по топикам для каждого университета.
    4. Возвращаем топ университетов (лимит не более 50).
    """
    return await service.recommend_organizations_by_topic_coefficients(
        db=db,
        query=query,
        limit=min(limit, MAX_RESULTS_LIMIT),
        top_topics=top_topics,
    )


