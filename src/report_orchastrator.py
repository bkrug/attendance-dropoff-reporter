import json
import os
from dataclasses import asdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from planning_center_client import PlanningCenterClient
from attendance_decline_accumulator import AttendanceDeclineAccumulator

class ReportOrchastrator:
    def __init__(self):
        httpClient = PlanningCenterClient()
        self._accumulator = AttendanceDeclineAccumulator(httpClient)

    def generate_report(self):
        group_name = os.getenv("GROUP_NAME")
        comparison_size_weeks = int(os.getenv("COMPARISON_SIZE_WEEKS", "26"))
        decline_threshold = float(os.getenv("DECLINE_THRESHOLD", ".20"))

        EASTERN = ZoneInfo("America/New_York")

        now_eastern = datetime.now(EASTERN)
        days_until_saturday = (5 - now_eastern.weekday()) % 7
        saturday_date = (now_eastern + timedelta(days=days_until_saturday)).date()
        end_date = datetime(saturday_date.year, saturday_date.month, saturday_date.day, tzinfo=EASTERN)
        middle_date = end_date - timedelta(days=comparison_size_weeks * 7 - 1)
        start_date = middle_date - timedelta(days=comparison_size_weeks * 7)

        print(start_date, middle_date, end_date)

        attendance_report = self._accumulator.get_members_with_declining_attendance(
            group_name, start_date, middle_date, end_date, decline_threshold
        )

        if attendance_report.error_message==None:
            with open("test_output/attendance_report.txt", "w") as f:
                f.write(json.dumps([asdict(member) for member in attendance_report.members], indent=2))
        else:
            print("Could not generate report: " + attendance_report.error_message)