from planning_center_client import PlanningCenterClient
from planning_center_models import GroupsGetResponse, GroupPeopleGetResponse, GroupEventsGetResponse, EventAttendancesGetResponse

class FakePlanningCenterClient(PlanningCenterClient):
    def __init__(
        self,
        group_response: GroupsGetResponse | None = None,
        people_responses: list[GroupPeopleGetResponse] | None = None,
        events_responses: list[GroupEventsGetResponse] | None = None,
        attendances_responses: dict[int, EventAttendancesGetResponse] | None = None,
    ):
        self._group_response = group_response
        self._people_responses = list(people_responses) if people_responses is not None else []
        self._events_responses = list(events_responses) if events_responses is not None else []
        self._attendances_responses = dict(attendances_responses) if attendances_responses is not None else []

    def get_group(self, group_name: str) -> GroupsGetResponse:
        return self._require(self._group_response, "group_response")

    def get_people(self, group_id: int, offset: int, page_size: int) -> GroupPeopleGetResponse:
        return self._require_next(self._people_responses, "people_responses")

    def get_events(self, group_id: int, earliest_date: str, latest_date: str, offset: int, page_size: int) -> GroupEventsGetResponse:
        return self._require_next(self._events_responses, "events_responses")

    def get_attendances(self, event_id: int, offset: int, page_size: int) -> EventAttendancesGetResponse:
        return self._require_key(self._attendances_responses, event_id, "attendances_responses")

    def _require(self, response, param_name: str):
        if response is None:
            raise NotImplementedError(f"FakePlanningCenterClient was not configured with {param_name}, but a test called the method that needs it.")
        return response

    def _require_next(self, responses: list, param_name: str):
        if not responses:
            raise NotImplementedError(f"FakePlanningCenterClient has no remaining {param_name}, but a test called the method that needs one.")
        return responses.pop(0)

    def _require_key(self, given_dict: dict, key: int, param_name: str):
        if not key in given_dict.keys():
            raise NotImplementedError(f"FakePlanningCenterClient has no {param_name} with key {key}, but a test called the method that needs one.")
        return given_dict[key]
