from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, get_organization_topic_service
from app.schemas.organization_topic import (
    OrganizationTopicCoefficientRequest,
    OrganizationTopicCoefficientResponse,
)
from app.services.organization_topic_service import OrganizationTopicService


router = APIRouter(prefix="/organization-topics", tags=["organization_topics"])


@router.post(
    "/recalculate",
    response_model=OrganizationTopicCoefficientResponse,
    summary="Пересчитать коэффициент для пары (organization, topic)",
)
async def recalculate_coefficient(
    payload: OrganizationTopicCoefficientRequest,
    db: AsyncSession = Depends(get_db_session),
    service: OrganizationTopicService = Depends(get_organization_topic_service),
) -> OrganizationTopicCoefficientResponse:
    """
    Пересчитывает и сохраняет коэффициент для пары (organization_id, topic_num)
    в таблице organization_topic.

    Алгоритм вычисления инкапсулирован в стратегии внутри OrganizationTopicService,
    поэтому его легко заменить.
    """
    obj = await service.recalculate_for_pair(
        db=db,
        organization_id=payload.organization_id,
        topic_num=payload.topic_num,
    )
    return OrganizationTopicCoefficientResponse.model_validate(obj)


@router.post(
    "/recalculate-all",
    response_model=List[OrganizationTopicCoefficientResponse],
    summary="Пересчитать коэффициенты для всех пар (organization, topic)",
)
async def recalculate_all_coefficients(
    db: AsyncSession = Depends(get_db_session),
    service: OrganizationTopicService = Depends(get_organization_topic_service),
) -> List[OrganizationTopicCoefficientResponse]:
    """
    Пересчитывает коэффициенты для всех пар (organization_id, topic_num),
    которые встречаются в данных (author, publication, publication_author),
    и сохраняет их в таблице organization_topic.

    Алгоритм вычисления также инкапсулирован в стратегии OrganizationTopicService.
    """
    objs = await service.recalculate_all(db=db)
    return [OrganizationTopicCoefficientResponse.model_validate(obj) for obj in objs]

