from src.report_models import MemberAttendance, DeclineReport

class AttendanceDeclineAccumulator:
    def get_members_with_declining_attendance() -> DeclineReport:
        return DeclineReport()