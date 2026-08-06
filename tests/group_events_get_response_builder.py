from datetime import datetime, timedelta
from planning_center_models import GroupEventsGetResponse
from planning_center_models.events import EventDatum, EventAttributes, EventImage, EventRelationships
from planning_center_models.common import DatumLinks, ResponseLinks, Relationship
from .meta_builder import MetaBuilder

class GroupEventsGetResponseBuilder:
    def __init__(self):
        self._events: list[EventDatum] = []
        self._meta_builder = MetaBuilder(parent_id=1, parent_type="Group")

    def add_event(self, event_id: int, starts_at: datetime) -> "GroupEventsGetResponseBuilder":
        ends_at = starts_at + timedelta(hours=1)
        self._events.append(
            EventDatum(
                type="Event",
                id=event_id,
                attributes=EventAttributes(
                    attendance_requests_enabled=False,
                    automated_reminder_enabled=False,
                    canceled=False,
                    canceled_at=None,
                    description=None,
                    ends_at=ends_at,
                    image=EventImage(thumbnail=None, medium=None, original=None),
                    location_type_preference="physical",
                    multi_day=False,
                    name="Test Event",
                    reminders_sent=False,
                    reminders_sent_at=None,
                    repeating=False,
                    starts_at=starts_at,
                    virtual_location_url=None,
                    visitors_count=None,
                ),
                relationships=EventRelationships(
                    attendance_submitter=Relationship(data=None),
                    group=Relationship(data=None),
                    location=Relationship(data=None),
                    repeating_event=Relationship(data=None),
                ),
                links=DatumLinks(),
            )
        )
        return self

    def add_next(self, next_offset: int, total_count: int) -> "GroupEventsGetResponseBuilder":
        self._meta_builder.add_next(next_offset, total_count)
        return self

    def build(self) -> GroupEventsGetResponse:
        return GroupEventsGetResponse(
            links=ResponseLinks(links_self="https://api.planningcenteronline.com/groups/v2/groups/1/events"),
            data=list(self._events),
            included=[],
            meta=self._meta_builder.with_count(len(self._events)).build(),
        )
