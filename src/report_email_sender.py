import base64
import logging
import os
from io import BytesIO
from azure.communication.email import EmailClient

class ReportEmailSender:
    def send_report(self,
            excel_bytes: BytesIO,
            recipient_list: str,
            title: str,
            body_text: str):
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
                "subject": title,
                "plainText": body_text,
                "html": f"<html><p>{body_text}</p></html>",
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

    def send_error(self, error_message: str, recipient_list: str):
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
