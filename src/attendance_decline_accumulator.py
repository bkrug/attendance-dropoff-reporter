from report_models import MemberAttendance, DeclineReport
from planning_center_client import PlanningCenterClient

class AttendanceDeclineAccumulator:
    def __init__(
        self,
        planning_center_client: PlanningCenterClient
    ):
        self.http_client = planning_center_client
    
    def get_members_with_declining_attendance(self, group_name: str) -> DeclineReport:
        group_response = self.http_client.get_group(group_name)
        if group_response.meta.total_count==0:
            return DeclineReport("Group not found", [])
        group_id = group_response.data[0].id

        people = self.get_list_of_people(group_id)
        if len(people)==0:
            return DeclineReport("Group has no people", [])

        events = self.get_list_of_events(group_id)
        if len(events)==0:
            return DeclineReport("Group has no events (worship services)", [])

        attendance_by_people_id = {person.id: 0 for person in people}
        for event in events:
            attendances = self.get_list_of_attendances(event.id)
            for attendance in attendances:
                person_id = attendance.relationships.person.data.id
                if attendance.attributes.attended:
                    attendance_by_people_id[person_id] += 1

        return DeclineReport(None, [])

    #TODO: Prevent either of this methods from entering an infinite loop
    #TODO: Calculate start and end date better
    def get_list_of_events(self, group_id):
        events_response = self.http_client.get_events(group_id, '1900-01-01', '1901-01-01', 0, 25)
        events = list(events_response.data)
        while events_response.meta.next is not None:
            events_response = self.http_client.get_events(group_id, '1900-01-01', '1901-01-01', events_response.meta.next.offset, 25)
            events.extend(events_response.data)
        return events

    #TODO: Prevent either of this methods from entering an infinite loop
    def get_list_of_people(self, group_id):
        people_response = self.http_client.get_people(group_id, 0, 25)
        people = list(people_response.data)
        while people_response.meta.next is not None:
            people_response = self.http_client.get_people(group_id, people_response.meta.next.offset, 25)
            people.extend(people_response.data)
        return people

    #TODO: Prevent either of this methods from entering an infinite loop
    def get_list_of_attendances(self, event_id):
        attendance_response = self.http_client.get_attendances(event_id, 0, 25)
        attendance = list(attendance_response.data)
        while attendance_response.meta.next is not None:
            attendance_response = self.http_client.get_attendances(event_id, attendance_response.meta.next.offset, 25)
            attendance.extend(attendance_response.data)
        return attendance