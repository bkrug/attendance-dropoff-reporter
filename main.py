from planning_center_client import PlanningCenterClient

httpClient = PlanningCenterClient()
people_data = httpClient.get_people(3017831, 0, 25)

print(len(people_data.data))
print(people_data.meta.count)
print(people_data.meta.total_count)

event_data = httpClient.get_events(3017831, '2026-06-01', '2026-08-08', 200)
print(len(event_data.data))
print(event_data.meta.total_count)