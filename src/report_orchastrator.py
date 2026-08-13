import base64
import json
import logging
import os
from dataclasses import asdict
from datetime import datetime, timedelta
from io import BytesIO
from zoneinfo import ZoneInfo
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
from planning_center_client import PlanningCenterClient
from attendance_decline_accumulator import AttendanceDeclineAccumulator
from report_models import MemberAttendance
from azure.communication.email import EmailClient
from dotenv import load_dotenv

load_dotenv()

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

        attendance_report = self._accumulator.get_members_with_declining_attendance(
            group_name, start_date, middle_date, end_date, decline_threshold
        )

        excel_email_recipients = os.getenv("REPORT_EMAIL_RECIPIENTS", "")

        if attendance_report.error_message==None:
            excel_bytes = self._get_attendance_report_as_bytes(
                attendance_report.members,
                start_date,
                middle_date,
            )
            excel_file_path = os.getenv("REPORT_FILE_PATH", "")
            if excel_file_path:
                with open(excel_file_path, "wb") as excel_file:
                    excel_file.write(excel_bytes.getvalue())
            if excel_email_recipients:
                self._send_email(excel_bytes, excel_email_recipients, start_date, middle_date)
        else:
            logging.error("Could not generate report: " + attendance_report.error_message)
            if excel_email_recipients:
                self._send_error_email(attendance_report.error_message, excel_email_recipients)

    def _get_attendance_report_as_bytes(
            self,
            members: list[MemberAttendance],
            start_date: datetime,
            middle_date: datetime) -> BytesIO:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Declining Attendance"
        TITLE_ROW = 1
        HEADER_ROW = 3
        TITLE_FONT_SIZE = 16

        headers = [
            "First Name",
            "Last Name",
            "Early Period Attendance",
            "Worship Day Count",
            "Early Period Frequency",
            "Late Period Attendance",
            "Worship Day Count",
            "Late Period Frequency",
            "Frequency Change",
        ]        

        title = self.get_title(start_date, middle_date)
        title_cell = sheet.cell(row=TITLE_ROW, column=1, value=title)
        sheet.merge_cells(start_row=TITLE_ROW, start_column=1, end_row=TITLE_ROW, end_column=len(headers))
        title_cell.alignment = Alignment(horizontal="center")
        # No name= set here, matching Font(bold=True) below (also no name=), so both inherit the workbook's theme font.
        title_cell.font = Font(size=TITLE_FONT_SIZE)

        PERCENTAGE_FORMAT = "0%"
        PERCENTAGE_COLUMN_HEADERS = ["Early Period Frequency", "Late Period Frequency", "Frequency Change"]
        percentage_columns = [get_column_letter(headers.index(header) + 1) for header in PERCENTAGE_COLUMN_HEADERS]

        sheet.append([])
        sheet.append(headers)
        sheet.row_dimensions[HEADER_ROW].height = 30
        for column_index, cell in enumerate(sheet[HEADER_ROW], start=1):
            cell.font = Font(bold=True)
            cell.alignment = Alignment(wrap_text=True)
            sheet.column_dimensions[cell.column_letter].width = 16

        for member in members:
            row_index = sheet.max_row + 1
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
            for column_letter in percentage_columns:
                sheet[f"{column_letter}{row_index}"].number_format = PERCENTAGE_FORMAT

        excel_bytes = BytesIO()
        workbook.save(excel_bytes)
        return excel_bytes

    def get_title(self, start_date, middle_date):
        title = f"Attendance Comparison between Period Starting {start_date.date().isoformat()} and Period Starting {middle_date.date().isoformat()}"
        return title

    def _send_email(self,
            excel_bytes: BytesIO,
            recipient_list: str,
            start_date: datetime,
            middle_date: datetime):
        sender_address = os.getenv("REPORT_EMAIL_SENDER", "donotreply@example.com")

        message = {
            "senderAddress": sender_address,
            "recipients":  {
                "to": [
                    {"address": address.strip()}
                    for address in recipient_list.split(";")
                    if address.strip()
                ],
            },
            "content": {
                "subject": self.get_title(start_date, middle_date),
                "plainText": "Please see the attached attendance decline report.",
                "html": "<html><p>Please see the attached attendance decline report.</p></html>",
            },
            "attachments": [
                {
                    "contentInBase64": base64.b64encode(excel_bytes.getvalue()).decode("utf-8"),  # Base64 encoded contents of the attachment. Required.
                    "contentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # MIME type of the content being attached. Required.
                    "name": "attendanceDeclineReport.xlsx"  # Name of the attachment. Required.
                }
            ]
        }

        self._send_message(message)

    def _send_error_email(self, error_message: str, recipient_list: str):
        sender_address = os.getenv("REPORT_EMAIL_SENDER", "donotreply@example.com")

        body_lines = [
            f"Could not generate the attendance decline report: {error_message}",
            "",
            "Environment settings:",
            f"RATE_LIMIT_MAX_REQUESTS={os.getenv('RATE_LIMIT_MAX_REQUESTS', '')}",
            f"RATE_LIMIT_WINDOW_SECONDS={os.getenv('RATE_LIMIT_WINDOW_SECONDS', '')}",
            f"LOG_RESPONSE_TEXT={os.getenv('LOG_RESPONSE_TEXT', '')}",
            f"PAGE_SIZE_EVENTS={os.getenv('PAGE_SIZE_EVENTS', '')}",
            f"PAGE_SIZE_PEOPLE={os.getenv('PAGE_SIZE_PEOPLE', '')}",
            f"PAGE_SIZE_ATTENDANCE={os.getenv('PAGE_SIZE_ATTENDANCE', '')}",
            f"GROUP_NAME={os.getenv('GROUP_NAME', '')}",
            f"COMPARISON_SIZE_WEEKS={os.getenv('COMPARISON_SIZE_WEEKS', '')}",
            f"DECLINE_THRESHOLD={os.getenv('DECLINE_THRESHOLD', '')}",
        ]

        message = {
            "senderAddress": sender_address,
            "recipients":  {
                "to": [
                    {"address": address.strip()}
                    for address in recipient_list.split(";")
                    if address.strip()
                ],
            },
            "content": {
                "subject": "Attendance report generation failed",
                "plainText": "\n".join(body_lines),
            },
        }

        self._send_message(message)

    def _send_message(self, message: dict):
        connection_string = os.getenv("AZURE_EMAIL_SERVICE_CONNECTION_STRING", "")

        POLLER_WAIT_TIME = 10

        try:
            email_client = EmailClient.from_connection_string(connection_string)

            poller = email_client.begin_send(message);

            time_elapsed = 0
            while not poller.done():
                logging.info("Email send poller status: " + poller.status())

                poller.wait(POLLER_WAIT_TIME)
                time_elapsed += POLLER_WAIT_TIME

                if time_elapsed > 18 * POLLER_WAIT_TIME:
                    raise RuntimeError("Polling timed out.")

            if poller.result()["status"] == "Succeeded":
                logging.info(f"Successfully sent the email (operation id: {poller.result()['id']})")
            else:
                raise RuntimeError(str(poller.result()["error"]))

        except Exception as ex:
            logging.exception(ex)