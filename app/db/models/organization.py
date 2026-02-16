from sqlalchemy import Column, Integer, String

from app.db.base import Base


class Organization(Base):
    """
    Таблица organization:
    - id
    - name
    - scopus_id
    - country_id
    - sector_id
    """

    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    scopus_id = Column(String, nullable=True, index=True)
    country_id = Column(Integer, nullable=True, index=True)
    sector_id = Column(Integer, nullable=True, index=True)

