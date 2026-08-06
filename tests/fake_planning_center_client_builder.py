from planning_center_models import GroupsGetResponse, GroupPeopleGetResponse, GroupEventsGetResponse, EventAttendancesGetResponse
from .fake_planning_center_client import FakePlanningCenterClient

class FakePlanningCenterClientBuilder:
    def __init__(self):
        self._group_response: GroupsGetResponse | None = None
        self._people_responses: list[GroupPeopleGetResponse] = []
        self._events_responses: list[GroupEventsGetResponse] = []
        self._attendances_responses: list[EventAttendancesGetResponse] = []

    def with_group_response(self, group_response: GroupsGetResponse) -> "FakePlanningCenterClientBuilder":
        self._group_response = group_response
        return self

    def add_people_response(self, people_response: GroupPeopleGetResponse) -> "FakePlanningCenterClientBuilder":
        self._people_responses.append(people_response)
        return self

    def add_events_response(self, events_response: GroupEventsGetResponse) -> "FakePlanningCenterClientBuilder":
        self._events_responses.append(events_response)
        return self

    def add_attendances_response(self, attendances_response: EventAttendancesGetResponse) -> "FakePlanningCenterClientBuilder":
        self._attendances_responses.append(attendances_response)
        return self

    def build(self) -> FakePlanningCenterClient:
        return FakePlanningCenterClient(
            group_response=self._group_response,
            people_responses=list(self._people_responses),
            events_responses=list(self._events_responses),
            attendances_responses=list(self._attendances_responses),
        )
