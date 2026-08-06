import requests
from dotenv import load_dotenv
import os

load_dotenv()

class PlanningCenterClient:
    def __init__(self):
        # Raise an error if either of these values is blank
        self.api_client_id = os.getenv("PLANNING_CENTER_CLIENT_ID")
        self.api_secret = os.getenv("PLANNING_CENTER_SECRET")

    def get_people(self, group_id: int) -> None:
        print("got here")
        url = f"https://api.planningcenteronline.com/groups/v2/groups/{group_id}/people?per_page=3"
        response = requests.get(url, auth=(self.api_client_id, self.api_secret))

        print(response.status_code)
        with open("people_response.txt", "w") as f:
            f.write(response.text)
