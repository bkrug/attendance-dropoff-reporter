from pydantic import BaseModel, ConfigDict, Field
from typing import List, Any
from datetime import datetime

class EmailAddress(BaseModel):
    address: str
    location: str
    primary: bool

class PhoneNumber(BaseModel):
    number: str
    carrier: str | None
    location: str
    primary: bool

class PersonAttributes(BaseModel):
    addresses: List[Any]
    avatar_url: str
    created_at: datetime
    email_addresses: List[EmailAddress]
    first_name: str
    gender: str | None
    last_name: str
    permissions: str
    phone_numbers: List[PhoneNumber]

class DatumLinks(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    links_self: str = Field(alias="self")
    html: str

class PersonDatum(BaseModel):
    type: str
    id: int
    attributes: PersonAttributes
    links: DatumLinks

class ResponseLinks(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    links_self: str = Field(alias="self")
    next: str

class Next(BaseModel):
    offset: int

class Parent(BaseModel):
    id: int
    type: str

class Meta(BaseModel):
    total_count: int
    count: int
    next: Next
    can_order_by: List[str]
    can_query_by: List[str]
    parent: Parent

class GroupPeopleGetResponse(BaseModel):
    links: ResponseLinks
    data: List[PersonDatum]
    included: List[Any]
    meta: Meta