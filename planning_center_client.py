import requests
import os
from dotenv import load_dotenv
from models import GroupPeopleGetResponse

load_dotenv()

class PlanningCenterClient:
    def __init__(self):
        # TODO: Raise an error if either of these values is blank
        self.api_client_id = os.getenv("PLANNING_CENTER_CLIENT_ID")
        self.api_secret = os.getenv("PLANNING_CENTER_SECRET")

    def get_people(self, group_id: int, offset: int, page_size: int) -> GroupPeopleGetResponse:
        url = f"https://api.planningcenteronline.com/groups/v2/groups/{group_id}/people?offset={offset}&per_page={page_size}"
        response = requests.get(url, auth=(self.api_client_id, self.api_secret))

        print(response.status_code)
        with open("people_response.txt", "w") as f:
            f.write(response.text)

        # TODO: Log serialization errors including location
        return GroupPeopleGetResponse.model_validate_json(response.text)
