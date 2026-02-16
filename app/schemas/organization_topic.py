from pydantic import BaseModel


class OrganizationTopicBase(BaseModel):
    organization_id: int
    topic_num: int


class OrganizationTopicCoefficientRequest(OrganizationTopicBase):
    """
    Запрос на пересчёт коэффициента для пары (organization, topic).
    """


class OrganizationTopicCoefficientResponse(OrganizationTopicBase):
    coefficient: float

    class Config:
        from_attributes = True

