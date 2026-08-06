from planning_center_client import PlanningCenterClient

httpClient = PlanningCenterClient()
people_data = httpClient.get_people(3017831)

print(len(people_data.data))
print(people_data.meta.count)
print(people_data.meta.total_count)