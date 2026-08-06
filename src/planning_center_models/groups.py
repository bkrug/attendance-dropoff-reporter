from pydantic import BaseModel
from typing import List, Any
from datetime import datetime
from .common import DatumLinks, ResponseLinks, Meta, Relationship

class GroupImage(BaseModel):
    thumbnail: str | None
    medium: str | None
    original: str | None

class GroupAttributes(BaseModel):
    archived_at: datetime | None
    chat_enabled: bool
    contact_email: str | None
    created_at: datetime
    description: str | None
    description_as_plain_text: str | None
    direct_messages_enabled: bool
    events_listed: bool
    events_visibility: str
    header_image: GroupImage
    leaders_can_search_people_database: bool
    listed: bool
    location_type_preference: str
    members_are_confidential: bool
    memberships_count: int
    name: str
    public_church_center_web_url: str | None
    schedule: str | None
    virtual_location_url: str | None

class GroupRelationships(BaseModel):
    group_type: Relationship
    location: Relationship

class GroupDatum(BaseModel):
    type: str
    id: int
    attributes: GroupAttributes
    relationships: GroupRelationships
    links: DatumLinks

class GroupsGetResponse(BaseModel):
    links: ResponseLinks
    data: List[GroupDatum]
    included: List[Any]
    meta: Meta
