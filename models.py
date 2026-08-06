from pydantic import BaseModel, Field
from typing import List, Any
from datetime import datetime

class EmailAddress(BaseModel):
    address: str
    location: str
    primary: bool

class PhoneNumber(BaseModel):
    number: str
    carrier: None
    location: str
    primary: bool

class PersonAttributes(BaseModel):
    addresses: List[Any]
    avatar_url: str
    created_at: datetime
    email_addresses: List[EmailAddress]
    first_name: str
    gender: str
    last_name: str
    permissions: str
    phone_numbers: List[PhoneNumber]

class DatumLinks(BaseModel):
    Field(alias="self")
    links_self: str
    html: str

class PersonDatum(BaseModel):
    type: str
    id: int
    attributes: PersonAttributes
    links: DatumLinks

class ResponseLinks(BaseModel):
    links_self: str
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