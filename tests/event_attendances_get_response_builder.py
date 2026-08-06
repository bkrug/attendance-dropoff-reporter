from planning_center_models import EventAttendancesGetResponse
from planning_center_models.attendances import AttendanceDatum, AttendanceAttributes, AttendanceRelationships
from planning_center_models.common import DatumLinks, ResponseLinks, Parent, Relationship
from .meta_builder import MetaBuilder

class EventAttendancesGetResponseBuilder:
    def __init__(self):
        self._attendances: list[AttendanceDatum] = []
        self._meta_builder = MetaBuilder(parent_id=1, parent_type="Event")

    def add_attendance(self, person_id: int, attended: bool) -> "EventAttendancesGetResponseBuilder":
        self._attendances.append(
            AttendanceDatum(
                type="Attendance",
                id=len(self._attendances) + 1,
                attributes=AttendanceAttributes(
                    attended=attended,
                    role="member",
                ),
                relationships=AttendanceRelationships(
                    person=Relationship(data=Parent(id=person_id, type="Person")),
                    event=Relationship(data=None),
                ),
                links=DatumLinks(),
            )
        )
        return self

    def with_next(self, next_offset: int, total_count: int) -> "EventAttendancesGetResponseBuilder":
        self._meta_builder.with_next(next_offset, total_count)
        return self

    def build(self) -> EventAttendancesGetResponse:
        return EventAttendancesGetResponse(
            links=ResponseLinks(links_self="https://api.planningcenteronline.com/groups/v2/events/1/attendances"),
            data=list(self._attendances),
            included=[],
            meta=self._meta_builder.with_count(len(self._attendances)).build(),
        )
