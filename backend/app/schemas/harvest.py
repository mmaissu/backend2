from pydantic import BaseModel
from typing import List, Optional


class HarvestArticle(BaseModel):
    openalex_id: str
    title: str
    authors: List[str]
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    cited_by_count: Optional[int] = None


class HarvestResponse(BaseModel):
    query: str
    count: int
    results: List[HarvestArticle]


class ImportArticleRequest(BaseModel):
    openalex_id: str


class ImportArticleResponse(BaseModel):
    message: str
    article_id: str | None = None