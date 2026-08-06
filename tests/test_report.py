# content of test_sysexit.py
import pytest
from planning_center_client import PlanningCenterClient
from planning_center_models import GroupsGetResponse, GroupPeopleGetResponse, GroupEventsGetResponse, EventAttendancesGetResponse
from .groups_get_response_builder import GroupsGetResponseBuilder
from attendance_decline_accumulator import AttendanceDeclineAccumulator

class FakePlanningCenterClient(PlanningCenterClient):
    def __init__(
        self,
        group_response: GroupsGetResponse | None = None,
        people_response: GroupPeopleGetResponse | None = None,
        events_response: GroupEventsGetResponse | None = None,
        attendances_response: EventAttendancesGetResponse | None = None,
    ):
        self._group_response = group_response
        self._people_response = people_response
        self._events_response = events_response
        self._attendances_response = attendances_response

    def get_group(self, group_name: str) -> GroupsGetResponse:
        return self._require(self._group_response, "group_response")

    def get_people(self, group_id: int, offset: int, page_size: int) -> GroupPeopleGetResponse:
        return self._require(self._people_response, "people_response")

    def get_events(self, group_id: int, earliest_date: str, latest_date: str, offset: int, page_size: int) -> GroupEventsGetResponse:
        return self._require(self._events_response, "events_response")

    def get_attendances(self, event_id: int, offset: int, page_size: int) -> EventAttendancesGetResponse:
        return self._require(self._attendances_response, "attendances_response")

    def _require(self, response, param_name: str):
        if response is None:
            raise NotImplementedError(f"FakePlanningCenterClient was not configured with {param_name}, but a test called the method that needs it.")
        return response

class TestReport:
    def testReport_groupDoesNotExist_expectErrorMsg(self):
        emptyGroupResponse = GroupsGetResponseBuilder().build()
        client = FakePlanningCenterClient(emptyGroupResponse)
        accumulator = AttendanceDeclineAccumulator(client)

        #Act
        actual_report = accumulator.get_members_with_declining_attendance("St. Lucas Attendance")

        #Assert
        assert actual_report.error_message=="Group not found"

    def testReport_groupExistsWithNoEvents_expectErrorMsg(self):
        groupResponse = GroupsGetResponseBuilder().add_group(1, "St. James Attendance").build()
        client = FakePlanningCenterClient(groupResponse)
        accumulator = AttendanceDeclineAccumulator(client)

        #Act
        actual_report = accumulator.get_members_with_declining_attendance("St. James Attendance")

        #Assert
        assert actual_report.error_message==None
