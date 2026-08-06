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
        if len(group_response.data)==0:
            return DeclineReport("Group not found", [])

        group_id = group_response.data[0].id
        events_response = self.http_client.get_events(group_id, '1900-01-01', '1901-01-01', 0, 25)
        if len(events_response.data)==0:
            return DeclineReport("Group has no events (worship services)", [])

        people_response = self.http_client.get_people(group_id, 0, 25)
        if len(people_response.data)==0:
            return DeclineReport("Group has no people", [])

        return DeclineReport(None, [])