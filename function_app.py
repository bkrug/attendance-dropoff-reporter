import os
import sys
import logging
import azure.functions as func

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from report_orchastrator import ReportOrchastrator
from report_email_sender import ReportEmailSender
from report_models import ReportingError

app = func.FunctionApp()

@app.timer_trigger(schedule="32 17 6 * * 2", arg_name="myTimer", run_on_startup=False,
              use_monitor=False)
def AttendanceTimedReport(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    try:
        logging.info('Python timer trigger function executed.')
        result = ReportOrchastrator().generate_report()
        if result.is_err():
            _handle_reporting_error(result.unwrap_err())
    except Exception as ex:
        _handle_failure(ex)

def _handle_reporting_error(error: ReportingError) -> None:
    logging.critical("Report generation failed: " + error.message)

    if error.send_error_email:
        recipients = os.getenv("REPORT_EMAIL_RECIPIENTS", "")
        if recipients:
            send_result = ReportEmailSender().send_error(error.message, recipients)
            if send_result.is_err():
                logging.critical("Failed to send failure notification email: " + send_result.unwrap_err().message)

def _handle_failure(ex: Exception) -> None:
    logging.critical("Unhandled exception in AttendanceTimedReport", exc_info=ex)

    try:
        recipients = os.getenv("REPORT_EMAIL_RECIPIENTS", "")
        if recipients:
            email_msg = "An uncaught exception occurred when attempting to generate an attendance report: " + str(ex)
            ReportEmailSender().send_error(email_msg, recipients)
    except Exception as email_ex:
        logging.critical("Failed to send failure notification email", exc_info=email_ex)
