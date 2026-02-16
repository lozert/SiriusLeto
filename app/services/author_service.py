from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.author_repository import author_repository
from app.schemas.author import AuthorCreate


class AuthorService:
    def __init__(self):
        self.repo = author_repository
        self.logger = get_logger(self.__class__.__name__)

    async def create_author(self, db: AsyncSession, author_in: AuthorCreate):
        self.logger.info("Creating author: %s", author_in.name)
        return await self.repo.create(db, author_in)

    async def list_authors(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        self.logger.debug("Listing authors skip=%s limit=%s", skip, limit)
        return await self.repo.list(db, skip=skip, limit=limit)

