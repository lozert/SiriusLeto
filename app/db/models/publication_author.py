from sqlalchemy import Column, ForeignKey, Integer

from app.db.base import Base


class PublicationAuthor(Base):
    """
    Таблица publication_author:
    - publication_id
    - author_id
    (составной первичный ключ)
    """

    __tablename__ = "publication_author"

    publication_id = Column(Integer, ForeignKey("publication.id"), primary_key=True)
    author_id = Column(Integer, ForeignKey("author.id"), primary_key=True)

