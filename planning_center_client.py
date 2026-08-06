import requests
from dotenv import load_dotenv
import os

load_dotenv()

class PlanningCenterClient:
    def __init__(self, s):
        print("inside the simple constructor")
        self.api_client_id = os.getenv("PLANNING_CENTER_CLIENT_ID")
        self.api_secret = os.getenv("PLANNING_CENTER_SECRET")

    def get_people(self, group_id: int) -> None:
        url = f"https://api.planningcenteronline.com/groups/v2/groups/{group_id}/people?per_page=3"
        response = requests.get(url, auth=(self.api_client_id, self.api_secret))

        with open("people_response.txt", "w") as f:
            f.write(response.text)
