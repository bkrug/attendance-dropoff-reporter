# content of test_sysexit.py
import pytest
from datetime import datetime
from .groups_get_response_builder import GroupsGetResponseBuilder
from .group_events_get_response_builder import GroupEventsGetResponseBuilder
from .group_people_get_response_builder import GroupPeopleGetResponseBuilder
from .event_attendances_get_response_builder import EventAttendancesGetResponseBuilder
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
        groupResponse = GroupsGetResponseBuilder().add_group(20, "St. James Attendance").build()
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

    def testReport_groupExistsWithData_expectSomeResults(self):
        ATTENDANCE_STEADY_HIGH = 101
        ATTENDANCE_STEADY_LOW = 105
        ATTENDANCE_NEVER = 103
        ATTENDANCE_INCREASE = 107
        ATTENDANCE_DECREASE_SMALL = 106
        ATTENDANCE_DECREASE_MEDIUM = 102
        ATTENDANCE_DECREASE_HIGH = 104

        groupResponse = GroupsGetResponseBuilder().add_group(10, "Trinity Attendance").build()
        peopleResponse1 = (
            GroupPeopleGetResponseBuilder()
            .add_person(ATTENDANCE_STEADY_HIGH, "Adicus", "Adams")
            .add_person(ATTENDANCE_DECREASE_MEDIUM, "Bill", "Birmingham")
            .add_person(ATTENDANCE_NEVER, "Cathy", "Clinton")
            .with_next(3, 7)
            .build()
        )
        peopleResponse2 = (
            GroupPeopleGetResponseBuilder()
            .add_person(ATTENDANCE_DECREASE_HIGH, "Dwanye", "Doe")
            .add_person(ATTENDANCE_STEADY_LOW, "Ed", "Edison")
            .add_person(ATTENDANCE_DECREASE_SMALL, "Frank", "Finch")
            .with_next(6, 7)
            .build()
        )
        peopleResponse3 = (
            GroupPeopleGetResponseBuilder()
            .add_person(ATTENDANCE_INCREASE, "Gerald", "Gibson")
            .with_next(None, 7)
            .build()
        )
        eventsResponse1 = (
            GroupEventsGetResponseBuilder()
            # First 4-week period
            .add_event(1001, datetime(2026, 7, 5, 9, 30))
            .add_event(1002, datetime(2026, 7, 5, 11, 30))
            .add_event(1011, datetime(2026, 7, 12, 9, 30))
            .add_event(1012, datetime(2026, 7, 12, 11, 30))
            .add_event(1021, datetime(2026, 7, 19, 9, 30))
            .add_event(1022, datetime(2026, 7, 19, 11, 30))
            .add_event(1031, datetime(2026, 7, 26, 9, 30))
            .add_event(1032, datetime(2026, 7, 26, 11, 30))
            # Second 4-week period
            .add_event(1101, datetime(2026, 8, 2, 9, 30))
            .add_event(1102, datetime(2026, 8, 2, 11, 30))
            .with_next(10, 16)
            .build()
        )
        eventsResponse2 = (
            GroupEventsGetResponseBuilder()
            .add_event(1111, datetime(2026, 7, 5, 9, 30))
            .add_event(1112, datetime(2026, 7, 5, 11, 30))
            .add_event(1121, datetime(2026, 7, 12, 9, 30))
            .add_event(1122, datetime(2026, 7, 12, 11, 30))
            .add_event(1131, datetime(2026, 7, 19, 9, 30))
            .add_event(1132, datetime(2026, 7, 19, 11, 30))
            .with_next(None, 16)
            .build()
        )
        SERVICE_9_30_MODULUS = 0
        SERVICE_11_30_MODULUS = 1

        goes_to_9_30 = [ATTENDANCE_STEADY_LOW, ATTENDANCE_INCREASE, ATTENDANCE_DECREASE_SMALL, ATTENDANCE_DECREASE_HIGH]
        goes_to_11_30 = [ATTENDANCE_STEADY_HIGH, ATTENDANCE_INCREASE, ATTENDANCE_DECREASE_MEDIUM]

        allEventIds = (
            [event.id for event in eventsResponse1.data] +
            [event.id for event in eventsResponse2.data]
        )

        attendanceBuildersByEventId = {eventId: EventAttendancesGetResponseBuilder() for eventId in allEventIds}

        #ATTENDANCE_NEVER
        for attendanceResponseBuilder in attendanceBuildersByEventId.values():
            attendanceResponseBuilder.add_attendance(ATTENDANCE_NEVER, False)

        #ATTENDANCE_STEADY_HIGH
        for attendanceResponseBuilder in attendanceBuildersByEventId.values():
            attendanceResponseBuilder.add_attendance(ATTENDANCE_STEADY_HIGH, True)

        #ATTENDANCE_STEADY_LOW
        attended_services = [1011, 1122]
        for eventId in attendanceBuildersByEventId.keys():
            attendanceBuildersByEventId[eventId].add_attendance(ATTENDANCE_STEADY_LOW, eventId in attended_services)

        client_builder = (
            FakePlanningCenterClientBuilder()
            .with_group_response(groupResponse)
            .add_people_response(peopleResponse1)
            .add_people_response(peopleResponse2)
            .add_people_response(peopleResponse3)
            .add_events_response(eventsResponse1)
            .add_events_response(eventsResponse2)
        )        
