from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, get_recommendation_service
from app.schemas.recommendation import (
    OrganizationRecommendation,
    OrganizationTopicAverageRecommendation,
)
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


@router.get(
    "/universities-by-coefficients",
    response_model=List[OrganizationTopicAverageRecommendation],
)
async def recommend_universities_by_coefficients(
    query: str = Query(
        ...,
        description=(
            "Куда пользователь хочет поступать / какая область интересует. "
            "Используется для выбора релевантных топиков."
        ),
    ),
    limit: int = Query(10, ge=1, le=100, description="Сколько университетов вернуть"),
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
    Рекомендует университеты на основе таблицы organization_topic:
    1. Ищем топики, подходящие под текст запроса пользователя (по названию).
    2. Берём коэффициенты (coefficient) для найденных топиков и университетов.
    3. Считаем средний коэффициент по выбранным топикам для каждого университета.
    4. Возвращаем топ университетов с наибольшим средним коэффициентом.

    Шаг «поиска ближайших топиков» можно позже заменить
    на настоящий векторный поиск по эмбеддингам тем.
    """
    return await service.recommend_organizations_by_topic_coefficients(
        db=db,
        query=query,
        limit=limit,
        top_topics=top_topics,
    )


