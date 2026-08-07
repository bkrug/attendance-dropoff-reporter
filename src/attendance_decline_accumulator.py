from report_models import MemberAttendance, DeclineReport
from planning_center_models import PersonDatum, EventDatum, AttendanceDatum
from planning_center_client import PlanningCenterClient
from operator import methodcaller
from datetime import datetime, date

class AttendanceDeclineAccumulator:
    def __init__(
        self,
        planning_center_client: PlanningCenterClient
    ):
        self.http_client = planning_center_client
    
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

        group_response = self.http_client.get_group(group_name)
        if group_response.meta.total_count==0:
            return DeclineReport("Group not found", [])
        group_id = group_response.data[0].id

        people = self._get_list_of_people(group_id)
        if len(people)==0:
            return DeclineReport("Group has no people", [])

        events = self._get_list_of_events(group_id, start_date, end_date)
        if len(events)==0:
            return DeclineReport("Group has no events (worship services)", [])

        early_events = self._group_events_by_date(event for event in events if event.attributes.starts_at < middle_date)
        late_events = self._group_events_by_date(event for event in events if event.attributes.starts_at >= middle_date)
        if len(early_events)==0:
            return DeclineReport("Group has no events in the early period", [])
        if len(late_events)==0:
            return DeclineReport("Group has no events in the late period", [])

        early_attendance = self._get_attendance_by_person_id(people, early_events)
        late_attendance = self._get_attendance_by_person_id(people, late_events)

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
        declining_attendance = sorted(
            (
                member_attendance
                for member_attendance
                in attendance_comparisons
                if member_attendance.frequency_change() < -decline_threshold
            ),
            key=methodcaller("frequency_change")
        )
        return DeclineReport(None, declining_attendance)

    # Claude code claims that we could remove this for-loop by using the itertools library.
    # "from itertools import groupby"
    # The problem is that it would only catch _consequtive_ matching keys.
    def _group_events_by_date(self, events: list[EventDatum]) -> dict[date, list[EventDatum]]:
        grouped: dict[date, list[EventDatum]] = {}
        for event in events:
            grouped.setdefault(event.attributes.starts_at.date(), []).append(event)
        return grouped

    def _get_attendance_by_person_id(self, people: list[PersonDatum], events_by_date: dict[date, list[EventDatum]]):
        attendance_by_people_id = {person.id: 0 for person in people}
        for cur_date in events_by_date.keys():
            list_of_attendances = [
                attendance
                for event in events_by_date[cur_date]
                for attendance in self._get_list_of_attendances(event.id)
            ]
            attendance_by_person_id = self._group_attendance_by_person_id(list_of_attendances)
            people_who_attended = [
                person_id
                for person_id, attended in attendance_by_person_id.items()
                if attended
            ]
            for person_id in people_who_attended:
                attendance_by_people_id[person_id] += 1
        return attendance_by_people_id

    def _group_attendance_by_person_id(self, attendances: list[AttendanceDatum]) -> dict[int, bool]:
        grouped: dict[int, bool] = {}
        for attendance in attendances:
            person_id = attendance.relationships.person.data.id
            grouped.setdefault(person_id, False)
            grouped[person_id] = grouped[person_id] or attendance.attributes.attended
        return grouped

    #TODO: Prevent either of this methods from entering an infinite loop
    #TODO: Page Size should somehow be configurable
    def _get_list_of_events(
            self,
            group_id: int,
            start_date: datetime,
            end_date: datetime
        ):
        earliest_date = start_date.date().isoformat()
        latest_date = end_date.date().isoformat()
        events_response = self.http_client.get_events(group_id, earliest_date, latest_date, 0, 25)
        events = list(events_response.data)
        while events_response.meta.next is not None:
            events_response = self.http_client.get_events(group_id, earliest_date, latest_date, events_response.meta.next.offset, 25)
            events.extend(events_response.data)
        return events

    #TODO: Prevent either of this methods from entering an infinite loop
    #TODO: Page Size should somehow be configurable
    def _get_list_of_people(self, group_id):
        people_response = self.http_client.get_people(group_id, 0, 25)
        people = list(people_response.data)
        while people_response.meta.next is not None:
            people_response = self.http_client.get_people(group_id, people_response.meta.next.offset, 25)
            people.extend(people_response.data)
        return people

    #TODO: Prevent either of this methods from entering an infinite loop
    #TODO: Page Size should somehow be configurable
    def _get_list_of_attendances(self, event_id):
        attendance_response = self.http_client.get_attendances(event_id, 0, 25)
        attendance = list(attendance_response.data)
        while attendance_response.meta.next is not None:
            attendance_response = self.http_client.get_attendances(event_id, attendance_response.meta.next.offset, 25)
            attendance.extend(attendance_response.data)
        return attendance