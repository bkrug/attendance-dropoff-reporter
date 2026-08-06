from pydantic import BaseModel
from typing import List, Any
from .common import DatumLinks, ResponseLinks, Meta, Relationship

class AttendanceAttributes(BaseModel):
    attended: bool
    role: str

class AttendanceRelationships(BaseModel):
    person: Relationship
    event: Relationship

class AttendanceDatum(BaseModel):
    type: str
    id: int
    attributes: AttendanceAttributes
    relationships: AttendanceRelationships
    links: DatumLinks

class EventAttendancesGetResponse(BaseModel):
    links: ResponseLinks
    data: List[AttendanceDatum]
    included: List[Any]
    meta: Meta
