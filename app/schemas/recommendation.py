from pydantic import BaseModel


class OrganizationRecommendation(BaseModel):
    organization_id: int
    organization_name: str
    topic: str
    publication_count: int

