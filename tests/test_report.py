# content of test_sysexit.py
import pytest
from datetime import datetime
from .groups_get_response_builder import GroupsGetResponseBuilder
from .group_events_get_response_builder import GroupEventsGetResponseBuilder
from .group_people_get_response_builder import GroupPeopleGetResponseBuilder
from .fake_planning_center_client_builder import FakePlanningCenterClientBuilder
from attendance_decline_accumulator import AttendanceDeclineAccumulator

class TestReport:
    def testReport_groupDoesNotExist_expectErrorMsg(self):
        emptyGroupResponse = GroupsGetResponseBuilder().build()
        client = FakePlanningCenterClientBuilder().with_group_response(emptyGroupResponse).build()
        accumulator = AttendanceDeclineAccumulator(client)

        #Act
        actual_report = accumulator.get_members_with_declining_attendance("St. Lucas Attendance")

        #Assert
        assert actual_report.error_message=="Group not found"

    def testReport_groupExistsWithNoPeople_expectErrorMsg(self):
        groupResponse = GroupsGetResponseBuilder().add_group(3, "St. Mark's Attendance").build()
        peopleResponse = GroupPeopleGetResponseBuilder().build()
        eventsResponse = GroupEventsGetResponseBuilder().add_event(10, datetime(2026, 8, 2, 9, 30)).build()
        client = (
            FakePlanningCenterClientBuilder()
            .with_group_response(groupResponse)
            .add_people_response(peopleResponse)
            .add_events_response(eventsResponse)
            .build()
        )
        accumulator = AttendanceDeclineAccumulator(client)

        #Act
        actual_report = accumulator.get_members_with_declining_attendance("St. Mark's Attendance")

        #Assert
        assert actual_report.error_message=="Group has no people"

    def testReport_groupExistsWithNoEvents_expectErrorMsg(self):
        groupResponse = GroupsGetResponseBuilder().add_group(1, "St. James Attendance").build()
        peopleResponse = GroupPeopleGetResponseBuilder().add_person(100, "Jane", "Doe").build()
        eventsResponse = GroupEventsGetResponseBuilder().build()
        client = (
            FakePlanningCenterClientBuilder()
            .with_group_response(groupResponse)
            .add_people_response(peopleResponse)
            .add_events_response(eventsResponse)
            .build()
        )
        accumulator = AttendanceDeclineAccumulator(client)

        #Act
        actual_report = accumulator.get_members_with_declining_attendance("St. James Attendance")

        #Assert
        assert actual_report.error_message=="Group has no events (worship services)"
