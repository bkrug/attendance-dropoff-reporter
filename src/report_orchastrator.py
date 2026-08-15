import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from result import Err, Ok, Result
from planning_center_client import PlanningCenterClient
from attendance_decline_accumulator import AttendanceDeclineAccumulator
from excel_report_generator import ExcelReportGenerator
from report_email_sender import ReportEmailSender
from report_models import ReportingError
from dotenv import load_dotenv

load_dotenv()

class ReportOrchastrator:
    def __init__(self):
        httpClient = PlanningCenterClient()
        self._accumulator = AttendanceDeclineAccumulator(httpClient)
        self._excel_generator = ExcelReportGenerator()
        self._email_sender = ReportEmailSender()

    def generate_report(self) -> Result[None, ReportingError]:
        group_name = os.getenv("GROUP_NAME")
        comparison_size_weeks = int(os.getenv("COMPARISON_SIZE_WEEKS", "26"))
        decline_threshold = float(os.getenv("DECLINE_THRESHOLD", ".20"))
        excel_email_recipients = os.getenv("REPORT_EMAIL_RECIPIENTS", "")
        excel_file_path = os.getenv("REPORT_FILE_PATH", "")

        EASTERN = ZoneInfo("America/New_York")

        now_eastern = datetime.now(EASTERN)
        days_until_saturday = (5 - now_eastern.weekday()) % 7
        saturday_date = (now_eastern + timedelta(days=days_until_saturday)).date()
        end_date = datetime(saturday_date.year, saturday_date.month, saturday_date.day, tzinfo=EASTERN)
        middle_date = end_date - timedelta(days=comparison_size_weeks * 7 - 1)
        start_date = middle_date - timedelta(days=comparison_size_weeks * 7)

        attendance_report = self._accumulator.get_members_with_declining_attendance(
            group_name, start_date, middle_date, end_date, decline_threshold
        )

        if not attendance_report.error_message:
            title = self._get_title(start_date, middle_date)
            body_text = f"Attached is a report comparing attendance between two {comparison_size_weeks} week periods and showing any decline more significant than {decline_threshold*100}%."
            excel_bytes = self._excel_generator.generate(attendance_report.members, title)
            if excel_email_recipients:
                send_result = self._email_sender.send_report(excel_bytes, excel_email_recipients, title, body_text)
                if send_result.is_err():
                    return send_result
            if excel_file_path:
                with open(excel_file_path, "wb") as excel_file:
                    excel_file.write(excel_bytes.getvalue())
            return Ok(None)
        else:
            logging.error("Could not generate report: " + attendance_report.error_message)
            if excel_email_recipients:
                send_result = self._email_sender.send_error(attendance_report.error_message, excel_email_recipients)
            return Err(ReportingError(send_error_email=False, message=attendance_report.error_message))

    def _get_title(self, start_date, middle_date):
        title = f"Attendance Comparison between Period Starting {start_date.date().isoformat()} and Period Starting {middle_date.date().isoformat()}"
        return title
