from pydantic import BaseModel, ConfigDict, Field
from typing import List, Any
from datetime import datetime
from common import DatumLinks, ResponseLinks, Meta

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

class PersonDatum(BaseModel):
    type: str
    id: int
    attributes: PersonAttributes
    links: DatumLinks

class GroupPeopleGetResponse(BaseModel):
    links: ResponseLinks
    data: List[PersonDatum]
    included: List[Any]
    meta: Meta