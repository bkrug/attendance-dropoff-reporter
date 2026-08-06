from pydantic import BaseModel, ConfigDict, Field
from typing import List, Any
from datetime import datetime
from .common import DatumLinks, ResponseLinks, Meta, Relationship

class EventImage(BaseModel):
    thumbnail: str | None
    medium: str | None
    original: str | None

class EventAttributes(BaseModel):
    attendance_requests_enabled: bool
    automated_reminder_enabled: bool
    canceled: bool
    canceled_at: datetime | None
    description: str | None
    ends_at: datetime
    image: EventImage
    location_type_preference: str
    multi_day: bool
    name: str
    reminders_sent: bool
    reminders_sent_at: datetime | None
    repeating: bool
    starts_at: datetime
    virtual_location_url: str | None
    visitors_count: int | None

class EventRelationships(BaseModel):
    attendance_submitter: Relationship
    group: Relationship
    location: Relationship
    repeating_event: Relationship

class EventDatum(BaseModel):
    type: str
    id: int
    attributes: EventAttributes
    relationships: EventRelationships
    links: DatumLinks

class GroupEventsGetResponse(BaseModel):
    links: ResponseLinks
    data: List[EventDatum]
    included: List[Any]
    meta: Meta