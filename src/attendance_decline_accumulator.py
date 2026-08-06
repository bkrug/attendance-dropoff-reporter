from src.report_models import MemberAttendance, DeclineReport
from src.planning_center_client import PlanningCenterClient

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
        else:
            return DeclineReport(None, [])