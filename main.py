import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from planning_center_client import PlanningCenterClient

group_id = 3017831

httpClient = PlanningCenterClient()

#TODO: Get this from config
group_data = httpClient.get_group("Sure Foundation Attendance")

people_data = httpClient.get_people(group_id, 0, 25)
print(len(people_data.data))
print(people_data.meta.total_count)

event_data = httpClient.get_events(group_id, '2026-06-01', '2026-08-08', 0, 200)
print(len(event_data.data))
print(event_data.meta.total_count)

event_id = event_data.data[6].id
attendance_data = httpClient.get_attendances(event_id, 0, 25)
print(len(attendance_data.data))
print(attendance_data.meta.total_count)