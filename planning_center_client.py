import requests


class PlanningCenterClient:
    def get_people(self, group_id: int) -> None:
        url = f"https://api.planningcenteronline.com/groups/v2/groups/{group_id}/people?per_page=3"
        response = requests.get(url)

        with open("people_response.txt", "w") as f:
            f.write(response.text)
