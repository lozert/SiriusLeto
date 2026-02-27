from pydantic import BaseModel


class OrganizationRecommendation(BaseModel):
    organization_id: int
    organization_name: str
    topic: str
    publication_count: int


class OrganizationTopicAverageRecommendation(BaseModel):
    """
    Рекомендация университета на основе среднего коэффициента
    по выбранным топикам из таблицы organization_topic.
    """

    organization_id: int
    organization_name: str
    average_coefficient: float

