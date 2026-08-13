import os
from result import Err, Ok, Result
from report_models import MemberAttendance, DeclineReport
from planning_center_models import PersonDatum, EventDatum, AttendanceDatum, GroupsGetResponse
from planning_center_client import PlanningCenterClient
from operator import methodcaller
from datetime import datetime, date

class AttendanceDeclineAccumulator:
    def __init__(
        self,
        planning_center_client: PlanningCenterClient
    ):
        self.http_client = planning_center_client
        self.page_size_events = int(os.getenv("PAGE_SIZE_EVENTS", "100"))
        self.page_size_people = int(os.getenv("PAGE_SIZE_PEOPLE", "100"))
        self.page_size_attendance = int(os.getenv("PAGE_SIZE_ATTENDANCE", "100"))
    
    def get_members_with_declining_attendance(
            self,
            group_name: str,
            start_date: datetime,
            middle_date: datetime,
            end_date: datetime,
            decline_threshold: float
        ) -> DeclineReport:
        if not 0 <= decline_threshold <= 1:
            return DeclineReport("Decline threshold must be between 0 and 1", [])

        result = self.http_client.get_group(group_name).and_then(
            self._require_group_id
        ).and_then(
            lambda group_id: self._get_list_of_people(group_id).and_then(self._require_people).and_then(
                lambda people: self._get_list_of_events(group_id, start_date, end_date).and_then(self._require_events).and_then(
                    lambda events: self._compare_attendance(people, events, middle_date, decline_threshold)
                )
            )
        )

        if result.is_err():
            return DeclineReport(result.unwrap_err(), [])
        return DeclineReport(None, result.unwrap())

    def _require_group_id(self, group_response: GroupsGetResponse) -> Result[int, str]:
        if group_response.meta.total_count==0:
            return Err("Group not found")
        return Ok(group_response.data[0].id)

    def _require_people(self, people: list[PersonDatum]) -> Result[list[PersonDatum], str]:
        if len(people)==0:
            return Err("Group has no people")
        return Ok(people)

    def _require_events(self, events: list[EventDatum]) -> Result[list[EventDatum], str]:
        if len(events)==0:
            return Err("Group has no events (worship services)")
        return Ok(events)

    def _compare_attendance(
            self,
            people: list[PersonDatum],
            events: list[EventDatum],
            middle_date: datetime,
            decline_threshold: float
        ) -> Result[list[MemberAttendance], str]:
        early_events = self._group_events_by_date(event for event in events if event.attributes.starts_at < middle_date)
        late_events = self._group_events_by_date(event for event in events if event.attributes.starts_at >= middle_date)
        if len(early_events)==0:
            return Err("Group has no events in the early period")
        if len(late_events)==0:
            return Err("Group has no events in the late period")

        return self._get_attendance_by_person_id(people, early_events).and_then(
            lambda early_attendance: self._get_attendance_by_person_id(people, late_events).map(
                lambda late_attendance: self._build_declining_attendance(
                    people, early_events, late_events, early_attendance, late_attendance, decline_threshold
                )
            )
        )

    def _build_declining_attendance(
            self,
            people: list[PersonDatum],
            early_events: dict[date, list[EventDatum]],
            late_events: dict[date, list[EventDatum]],
            early_attendance: dict[int, int],
            late_attendance: dict[int, int],
            decline_threshold: float
        ) -> list[MemberAttendance]:
        attendance_comparisons = [
            MemberAttendance(
                person.attributes.first_name,
                person.attributes.last_name,
                early_attendance[person.id],
                len(early_events),
                late_attendance[person.id],
                len(late_events)
            )
            for person
            in people
        ]
        return sorted(
            (
                member_attendance
                for member_attendance
                in attendance_comparisons
                if member_attendance.frequency_change() <= -decline_threshold
            ),
            key=methodcaller("frequency_change")
        )

    # Claude code claims that we could remove this for-loop by using the itertools library.
    # "from itertools import groupby"
    # The problem is that it would only catch _consequtive_ matching keys.
    def _group_events_by_date(self, events: list[EventDatum]) -> dict[date, list[EventDatum]]:
        grouped: dict[date, list[EventDatum]] = {}
        for event in events:
            grouped.setdefault(event.attributes.starts_at.date(), []).append(event)
        return grouped

    def _get_attendance_by_person_id(
            self,
            people: list[PersonDatum],
            events_by_date: dict[date, list[EventDatum]]
        ) -> Result[dict[int, int], str]:
        attendance_by_people_id = {person.id: 0 for person in people}
        for cur_date in events_by_date.keys():
            list_of_attendances = []
            for event in events_by_date[cur_date]:
                attendances_result = self._get_list_of_attendances(event.id)
                if attendances_result.is_err():
                    return attendances_result
                list_of_attendances.extend(attendances_result.unwrap())

            attendance_by_person_id = self._group_attendance_by_person_id(list_of_attendances)
            people_who_attended = [
                person_id
                for person_id, attended in attendance_by_person_id.items()
                if attended and person_id in attendance_by_people_id.keys()
            ]
            for person_id in people_who_attended:
                attendance_by_people_id[person_id] += 1
        return Ok(attendance_by_people_id)

    def _group_attendance_by_person_id(self, attendances: list[AttendanceDatum]) -> dict[int, bool]:
        grouped: dict[int, bool] = {}
        for attendance in attendances:
            person_id = attendance.relationships.person.data.id
            grouped.setdefault(person_id, False)
            grouped[person_id] = grouped[person_id] or attendance.attributes.attended
        return grouped

    #TODO: Prevent either of this methods from entering an infinite loop
    def _get_list_of_events(
            self,
            group_id: int,
            start_date: datetime,
            end_date: datetime
        ) -> Result[list[EventDatum], str]:
        earliest_date = start_date.date().isoformat()
        latest_date = end_date.date().isoformat()
        events_response_result = self.http_client.get_events(group_id, earliest_date, latest_date, 0, self.page_size_events)
        if events_response_result.is_err():
            return events_response_result
        events_response = events_response_result.unwrap()
        events = list(events_response.data)
        while events_response.meta.next is not None:
            events_response_result = self.http_client.get_events(group_id, earliest_date, latest_date, events_response.meta.next.offset, self.page_size_events)
            if events_response_result.is_err():
                return events_response_result
            events_response = events_response_result.unwrap()
            events.extend(events_response.data)
        return Ok(events)

    #TODO: Prevent either of this methods from entering an infinite loop
    def _get_list_of_people(self, group_id) -> Result[list[PersonDatum], str]:
        people_response_result = self.http_client.get_people(group_id, 0, self.page_size_people)
        if people_response_result.is_err():
            return people_response_result
        people_response = people_response_result.unwrap()
        people = list(people_response.data)
        while people_response.meta.next is not None:
            people_response_result = self.http_client.get_people(group_id, people_response.meta.next.offset, self.page_size_people)
            if people_response_result.is_err():
                return people_response_result
            people_response = people_response_result.unwrap()
            people.extend(people_response.data)
        return Ok(people)

    #TODO: Prevent either of this methods from entering an infinite loop
    def _get_list_of_attendances(self, event_id) -> Result[list[AttendanceDatum], str]:
        attendance_response_result = self.http_client.get_attendances(event_id, 0, self.page_size_attendance)
        if attendance_response_result.is_err():
            return attendance_response_result
        attendance_response = attendance_response_result.unwrap()
        attendance = list(attendance_response.data)
        while attendance_response.meta.next is not None:
            attendance_response_result = self.http_client.get_attendances(event_id, attendance_response.meta.next.offset, self.page_size_attendance)
            if attendance_response_result.is_err():
                return attendance_response_result
            attendance_response = attendance_response_result.unwrap()
            attendance.extend(attendance_response.data)
        return Ok(attendance)