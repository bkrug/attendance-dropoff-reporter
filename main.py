import json
import os
import sys
from dataclasses import asdict
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from planning_center_client import PlanningCenterClient
from attendance_decline_accumulator import AttendanceDeclineAccumulator

EASTERN = ZoneInfo("America/New_York")

httpClient = PlanningCenterClient()
accumulator = AttendanceDeclineAccumulator(httpClient)

attendance_report = accumulator.get_members_with_declining_attendance(
    "Sure Foundation Attendance",
    datetime(2026, 5, 31, tzinfo=EASTERN),
    datetime(2026, 7, 5, tzinfo=EASTERN),
    datetime(2026, 8, 8, tzinfo=EASTERN),
    .10
)

if attendance_report.error_message==None:
    with open("test_output/attendance_report.txt", "w") as f:
        f.write(json.dumps([asdict(member) for member in attendance_report.members], indent=2))
else:
    print("Could not generate report: " + attendance_report.error_message)