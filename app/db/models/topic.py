from sqlalchemy import Column, Float, Integer, String

from app.db.base import Base


class Topic(Base):
    __tablename__ = "topic"

    num = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    prominence_percentile = Column(Float, nullable=True)

