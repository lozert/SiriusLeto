from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, get_author_service
from app.schemas.author import AuthorCreate, AuthorRead
from app.services.author_service import AuthorService


router = APIRouter(prefix="/authors", tags=["authors"])


@router.post("/", response_model=AuthorRead)
async def create_author(
    author_in: AuthorCreate,
    db: AsyncSession = Depends(get_db_session),
    service: AuthorService = Depends(get_author_service),
):
    return await service.create_author(db, author_in)


@router.get("/", response_model=List[AuthorRead])
async def list_authors(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    service: AuthorService = Depends(get_author_service),
):
    return await service.list_authors(db, skip=skip, limit=limit)

