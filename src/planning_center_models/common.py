from pydantic import BaseModel, ConfigDict, Field
from typing import List

class DatumLinks(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    links_self: str | None = Field(default=None, alias="self")
    html: str | None = None

class Next(BaseModel):
    offset: int

class Parent(BaseModel):
    id: int
    type: str

class Relationship(BaseModel):
    data: Parent | None

class ResponseLinks(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    links_self: str = Field(alias="self")
    next: str | None = None

class Meta(BaseModel):
    total_count: int
    count: int
    next: Next | None = None
    can_order_by: List[str]
    can_query_by: List[str]
    can_include: List[str] | None = None
    can_filter: List[str] | None = None
    onboarding: bool | None = None
    parent: Parent