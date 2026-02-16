from sqlalchemy import Column, Float, ForeignKey, Integer

from app.db.base import Base


class OrganizationTopic(Base):
    """
    Таблица для связи организации и темы с коэффициентом важности.

    Поля:
    - organization_id  (FK -> organization.id)
    - topic_num        (FK -> topic.num)
    - coefficient      (вес/коэффициент важности темы для организации)
    """

    __tablename__ = "organization_topic"

    organization_id = Column(Integer, ForeignKey("organization.id"), primary_key=True)
    topic_num = Column(Integer, ForeignKey("topic.num"), primary_key=True)
    coefficient = Column(Float, nullable=False)

