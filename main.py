import os
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from planning_center_client import PlanningCenterClient
from attendance_decline_accumulator import AttendanceDeclineAccumulator

httpClient = PlanningCenterClient()
accumulator = AttendanceDeclineAccumulator(httpClient)

attendance_report = accumulator.get_members_with_declining_attendance(
    "Sure Foundation Attendance",
    datetime(2026, 6, 1),
    datetime(2026, 7, 1),
    datetime(2026, 8, 31),
    .25
)

if attendance_report.error_message==None:
    with open("test_output/attendance_report.txt", "w") as f:
        f.write(attendance_report.members)
else:
    print("Could not generate report: " + attendance_report.error_message)