import json
import os
from dataclasses import asdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from openpyxl import Workbook
from openpyxl.styles import Font
from planning_center_client import PlanningCenterClient
from attendance_decline_accumulator import AttendanceDeclineAccumulator
from report_models import MemberAttendance

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
            self._write_attendance_report_to_excel(attendance_report.members, "test_output/attendance_report.xlsx")
        else:
            print("Could not generate report: " + attendance_report.error_message)

    def _write_attendance_report_to_excel(self, members: list[MemberAttendance], path: str) -> None:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Declining Attendance"

        headers = [
            "First Name",
            "Last Name",
            "Early Period Attendance",
            "Early Period Record Count",
            "Early Period Frequency",
            "Late Period Attendance",
            "Late Period Record Count",
            "Late Period Frequency",
            "Frequency Change",
        ]
        sheet.append(headers)
        for cell in sheet[1]:
            cell.font = Font(bold=True)

        for member in members:
            sheet.append([
                member.first_name,
                member.last_name,
                member.early_period_attendance,
                member.early_period_record_count,
                member.early_period_frequency(),
                member.late_period_attendance,
                member.late_period_record_count,
                member.late_period_frequency(),
                member.frequency_change(),
            ])

        workbook.save(path)