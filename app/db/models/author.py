from sqlalchemy import Column, ForeignKey, Integer, String

from app.db.base import Base


class Author(Base):
    """
    Таблица author:
    - id
    - name
    - scopus_id
    - h_index
    - organization_id
    """

    __tablename__ = "author"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    scopus_id = Column(String, nullable=True, index=True)
    h_index = Column(Integer, nullable=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=True, index=True)

