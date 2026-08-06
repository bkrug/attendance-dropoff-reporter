from planning_center_models import EventAttendancesGetResponse
from planning_center_models.attendances import AttendanceDatum, AttendanceAttributes, AttendanceRelationships
from planning_center_models.common import DatumLinks, ResponseLinks, Meta, Parent, Relationship

class EventAttendancesGetResponseBuilder:
    def __init__(self):
        self._attendances: list[AttendanceDatum] = []

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

    def build(self) -> EventAttendancesGetResponse:
        return EventAttendancesGetResponse(
            links=ResponseLinks(links_self="https://api.planningcenteronline.com/groups/v2/events/1/attendances"),
            data=list(self._attendances),
            included=[],
            meta=Meta(
                total_count=len(self._attendances),
                count=len(self._attendances),
                can_order_by=[],
                can_query_by=[],
                parent=Parent(id=1, type="Event"),
            ),
        )
