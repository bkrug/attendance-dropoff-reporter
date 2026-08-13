import os
import sys
import logging
import azure.functions as func

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from report_orchastrator import ReportOrchastrator

app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * 2", arg_name="myTimer", run_on_startup=True,
              use_monitor=False)
def AttendanceTimedReport(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
    ReportOrchastrator().generate_report()
