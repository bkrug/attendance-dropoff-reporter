from report_models import MemberAttendance, DeclineReport
from planning_center_client import PlanningCenterClient
from operator import methodcaller
from datetime import datetime

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
        group_response = self.http_client.get_group(group_name)
        if group_response.meta.total_count==0:
            return DeclineReport("Group not found", [])
        group_id = group_response.data[0].id

        people = self.get_list_of_people(group_id)
        if len(people)==0:
            return DeclineReport("Group has no people", [])

        events = self.get_list_of_events(group_id, start_date, end_date)
        if len(events)==0:
            return DeclineReport("Group has no events (worship services)", [])

        early_events = [event for event in events if event.attributes.starts_at < middle_date]
        late_events = [event for event in events if event.attributes.starts_at >= middle_date]

        early_attendance = self.get_attendance_by_person_id(people, early_events)
        late_attendance = self.get_attendance_by_person_id(people, late_events)

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

    def get_attendance_by_person_id(self, people, events):
        attendance_by_people_id = {person.id: 0 for person in people}
        for event in events:
            attendances = self.get_list_of_attendances(event.id)
            for attendance in (a for a in attendances if a.attributes.attended):
                person_id = attendance.relationships.person.data.id
                attendance_by_people_id[person_id] += 1
        return attendance_by_people_id

    #TODO: Prevent either of this methods from entering an infinite loop
    #TODO: Page Size should somehow be configurable
    def get_list_of_events(
            self,
            group_id: int,
            start_date: datetime,
            end_date: datetime
        ):
        events_response = self.http_client.get_events(group_id, start_date, end_date, 0, 25)
        events = list(events_response.data)
        while events_response.meta.next is not None:
            events_response = self.http_client.get_events(group_id, start_date, end_date, events_response.meta.next.offset, 25)
            events.extend(events_response.data)
        return events

    #TODO: Prevent either of this methods from entering an infinite loop
    #TODO: Page Size should somehow be configurable
    def get_list_of_people(self, group_id):
        people_response = self.http_client.get_people(group_id, 0, 25)
        people = list(people_response.data)
        while people_response.meta.next is not None:
            people_response = self.http_client.get_people(group_id, people_response.meta.next.offset, 25)
            people.extend(people_response.data)
        return people

    #TODO: Prevent either of this methods from entering an infinite loop
    #TODO: Page Size should somehow be configurable
    def get_list_of_attendances(self, event_id):
        attendance_response = self.http_client.get_attendances(event_id, 0, 25)
        attendance = list(attendance_response.data)
        while attendance_response.meta.next is not None:
            attendance_response = self.http_client.get_attendances(event_id, attendance_response.meta.next.offset, 25)
            attendance.extend(attendance_response.data)
        return attendance