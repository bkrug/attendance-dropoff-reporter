import requests
import os
from dotenv import load_dotenv
from planning_center_models import GroupPeopleGetResponse, GroupEventsGetResponse, EventAttendancesGetResponse, GroupsGetResponse

load_dotenv()

class PlanningCenterClient:
    def __init__(self):
        # TODO: Raise an error if either of these values is blank
        self.api_client_id = os.getenv("PLANNING_CENTER_CLIENT_ID")
        self.api_secret = os.getenv("PLANNING_CENTER_SECRET")
        os.makedirs("test_output", exist_ok=True)

    def get_group(self, group_name: str) -> GroupsGetResponse:
        url = f"https://api.planningcenteronline.com/groups/v2/groups?where[name]={group_name}"
        response = requests.get(url, auth=(self.api_client_id, self.api_secret))

        with open("test_output/group_response.txt", "w") as f:
            f.write(response.text)

        # TODO: Log serialization errors including location
        return GroupsGetResponse.model_validate_json(response.text)

    def get_people(self, group_id: int, offset: int, page_size: int) -> GroupPeopleGetResponse:
        url = f"https://api.planningcenteronline.com/groups/v2/groups/{group_id}/people?offset={offset}&per_page={page_size}"
        response = requests.get(url, auth=(self.api_client_id, self.api_secret))

        with open("test_output/people_response.txt", "w") as f:
            f.write(response.text)

        # TODO: Log serialization errors including location
        return GroupPeopleGetResponse.model_validate_json(response.text)

    def get_events(self, group_id: int, earliest_date: str, latest_date: str, offset: int, page_size: int) -> GroupEventsGetResponse:
        url = f"https://api.planningcenteronline.com/groups/v2/groups/{group_id}/events?order=starts_at&filter=not_canceled&where[starts_at][gte]={earliest_date}&where[ends_at][lte]={latest_date}&offset={offset}&per_page={page_size}"
        response = requests.get(url, auth=(self.api_client_id, self.api_secret))

        with open("test_output/event_response.txt", "w") as f:
            f.write(response.text)

        # TODO: Log serialization errors including location
        return GroupEventsGetResponse.model_validate_json(response.text)

    def get_attendances(self, event_id: int, offset: int, page_size: int) -> EventAttendancesGetResponse:
        url = f"https://api.planningcenteronline.com/groups/v2/events/{event_id}/attendances?offset={offset}&per_page={page_size}"
        response = requests.get(url, auth=(self.api_client_id, self.api_secret))

        with open("test_output/attendance_response.txt", "w") as f:
            f.write(response.text)

        return EventAttendancesGetResponse.model_validate_json(response.text)