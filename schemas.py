from typing import List, Optional, Literal
from pydantic import BaseModel

# Литерал для допустимых имен коллекций
collection_names_literal = Literal[
    "author_average", 
    "author_name", 
    "publication_name", 
    "organization_name", 
    "conference", 
    "journal_coll"
]

class MilvusGetDataDTO(BaseModel):
    collection_name: collection_names_literal
    ids: List[int]

class MilvusSearchDTO(BaseModel):
    collection_name: collection_names_literal
    embedding: List[float]
    expr: Optional[str] = None
    limit: Optional[int] = None
    output_fields: Optional[List[str]] = None