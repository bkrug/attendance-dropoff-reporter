# content of test_sysexit.py
import pytest
from datetime import datetime
from .groups_get_response_builder import GroupsGetResponseBuilder
from .group_events_get_response_builder import GroupEventsGetResponseBuilder
from .group_people_get_response_builder import GroupPeopleGetResponseBuilder
from .event_attendances_get_response_builder import EventAttendancesGetResponseBuilder
from .fake_planning_center_client_builder import FakePlanningCenterClientBuilder
from attendance_decline_accumulator import AttendanceDeclineAccumulator

def record_events_that_person_attended(
        attendanceBuildersByEventId: dict[int, EventAttendancesGetResponseBuilder],
        person_id: int,
        attended_event_ids
    ):
    for eventId in attendanceBuildersByEventId.keys():
        attendanceBuildersByEventId[eventId].add_attendance(person_id, eventId in attended_event_ids)


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

    def testReport_groupExistsWithData_expectReportComparingEarly4WeeksWithLate4Weeks(self):
        MEMBER_NEVER_ATTENDED = 103
        MEMBER_CONSISTENT_HIGH = 101
        MEMBER_CONSISTENT_LOW = 105
        MEMBER_ATTENDANCE_INCREASED = 107
        MEMBER_DECREASE_SMALL = 106
        MEMBER_DECREASE_MEDIUM = 102
        MEMBER_DECREASE_HIGH = 104
        DECREASE_MEDIUM_FIRST_NAME = "Bill"
        DECREASE_MEDIUM_LAST_NAME = "Birmingham"
        DECREASE_HIGH_FIRST_NAME = "Dwayne"
        DECREASE_HIGH_LAST_NAME = "Doe"

        group_name = "Trinity Attendance"
        groupResponse = GroupsGetResponseBuilder().add_group(10, group_name).build()
        peopleResponse1 = (
            GroupPeopleGetResponseBuilder()
            .add_person(MEMBER_CONSISTENT_HIGH, "Adicus", "Adams")
            .add_person(MEMBER_DECREASE_MEDIUM, DECREASE_MEDIUM_FIRST_NAME, DECREASE_MEDIUM_LAST_NAME)
            .add_person(MEMBER_NEVER_ATTENDED, "Cathy", "Clinton")
            .with_next(3, 7)
            .build()
        )
        peopleResponse2 = (
            GroupPeopleGetResponseBuilder()
            .add_person(MEMBER_DECREASE_HIGH, DECREASE_HIGH_FIRST_NAME, DECREASE_HIGH_LAST_NAME)
            .add_person(MEMBER_CONSISTENT_LOW, "Ed", "Edison")
            .add_person(MEMBER_DECREASE_SMALL, "Frank", "Finch")
            .with_next(6, 7)
            .build()
        )
        peopleResponse3 = (
            GroupPeopleGetResponseBuilder()
            .add_person(MEMBER_ATTENDANCE_INCREASED, "Gerald", "Gibson")
            .with_next(None, 7)
            .build()
        )
        eventsResponse1 = (
            GroupEventsGetResponseBuilder()
            # Early 4-week period
            .add_event(1001, datetime(2026, 7, 5, 9, 30))
            .add_event(1011, datetime(2026, 7, 12, 9, 30))
            .add_event(1021, datetime(2026, 7, 19, 9, 30))
            .add_event(1031, datetime(2026, 7, 26, 9, 30))
            # Late 4-week period
            .add_event(1101, datetime(2026, 8, 2, 9, 30))
            .with_next(5, 8)
            .build()
        )
        eventsResponse2 = (
            GroupEventsGetResponseBuilder()
            .add_event(1111, datetime(2026, 7, 5, 9, 30))
            .add_event(1121, datetime(2026, 7, 12, 9, 30))
            .add_event(1131, datetime(2026, 7, 19, 9, 30))
            .with_next(None, 8)
            .build()
        )

        allEventIds = (
            [event.id for event in eventsResponse1.data] +
            [event.id for event in eventsResponse2.data]
        )
        half_of_ids = int(len(allEventIds)/ 2)
        earlyPeriodEventIds = allEventIds[:half_of_ids]
        latePeriodEventIds = allEventIds[half_of_ids:]

        attendanceBuildersByEventId = {eventId: EventAttendancesGetResponseBuilder() for eventId in allEventIds}

        record_events_that_person_attended(attendanceBuildersByEventId, MEMBER_NEVER_ATTENDED, [])
        record_events_that_person_attended(attendanceBuildersByEventId, MEMBER_CONSISTENT_HIGH, allEventIds)
        record_events_that_person_attended(
            attendanceBuildersByEventId,
            MEMBER_CONSISTENT_LOW,
            [ earlyPeriodEventIds[1], latePeriodEventIds[3] ]
        )
        record_events_that_person_attended(
            attendanceBuildersByEventId,
            MEMBER_ATTENDANCE_INCREASED,
            [
                earlyPeriodEventIds[2],
                latePeriodEventIds[0],
                latePeriodEventIds[1],
                latePeriodEventIds[3]
            ]
        )
        record_events_that_person_attended(
            attendanceBuildersByEventId,
            MEMBER_DECREASE_SMALL,
            [
                earlyPeriodEventIds[0],
                earlyPeriodEventIds[1],
                earlyPeriodEventIds[2],
                earlyPeriodEventIds[3],
                latePeriodEventIds[0],
                latePeriodEventIds[2],
                latePeriodEventIds[3]
            ]
        )
        record_events_that_person_attended(
            attendanceBuildersByEventId,
            MEMBER_DECREASE_MEDIUM,
            [
                earlyPeriodEventIds[0],
                earlyPeriodEventIds[1],
                earlyPeriodEventIds[2],
                earlyPeriodEventIds[3],
                latePeriodEventIds[1],
                latePeriodEventIds[3]
            ]
        )
        record_events_that_person_attended(
            attendanceBuildersByEventId,
            MEMBER_DECREASE_HIGH,
            [
                earlyPeriodEventIds[0],
                earlyPeriodEventIds[1],
                earlyPeriodEventIds[2],
                earlyPeriodEventIds[3],
                latePeriodEventIds[2]
            ]
        )

        client_builder = (
            FakePlanningCenterClientBuilder()
            .with_group_response(groupResponse)
            .add_people_response(peopleResponse1)
            .add_people_response(peopleResponse2)
            .add_people_response(peopleResponse3)
            .add_events_response(eventsResponse1)
            .add_events_response(eventsResponse2)
        )
        for builder in attendanceBuildersByEventId.values():
            client_builder.add_attendances_response(builder.build())
        client = client_builder.build()
        accumulator = AttendanceDeclineAccumulator(client)

        # Act
        report = accumulator.get_members_with_declining_attendance(group_name)

        # Assert
        assert report.error_message==None
        assert len(report.members)==2
