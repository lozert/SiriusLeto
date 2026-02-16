from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from app.db.base import Base


class Publication(Base):
    """
    Таблица publication с полями:
    - id
    - name
    - type
    - abstract
    - english
    - pages_num
    - doi
    - eid
    - pubmed_id
    - views_num
    - citations_num
    - open_access
    - correspondence_address
    - date_year
    - topic_cluster_num
    - topic_num
    - publication_source_id
    """

    __tablename__ = "publication"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=True, index=True)
    abstract = Column(Text, nullable=True)
    english = Column(Boolean, nullable=True)
    pages_num = Column(Integer, nullable=True)
    doi = Column(String, nullable=True, index=True)
    eid = Column(String, nullable=True, index=True)
    pubmed_id = Column(String, nullable=True, index=True)
    views_num = Column(Integer, nullable=True)
    citations_num = Column(Integer, nullable=True)
    open_access = Column(Boolean, nullable=True)
    correspondence_address = Column(Text, nullable=True)
    date_year = Column(Integer, nullable=True, index=True)
    topic_cluster_num = Column(Integer, nullable=True, index=True)
    topic_num = Column(Integer, ForeignKey("topic.num"), nullable=True, index=True)
    publication_source_id = Column(Integer, nullable=True, index=True)

