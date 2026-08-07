import requests
import os
import sys
import time
from collections import deque
from http import HTTPStatus
from dotenv import load_dotenv
from planning_center_models import GroupPeopleGetResponse, GroupEventsGetResponse, EventAttendancesGetResponse, GroupsGetResponse

load_dotenv()

class PlanningCenterClient:
    #TODO: Make this configurable
    RATE_LIMIT_MAX_REQUESTS = 80
    RATE_LIMIT_WINDOW_SECONDS = 20

    def __init__(self):
        # TODO: Raise an error if either of these values is blank
        self.api_client_id = os.getenv("PLANNING_CENTER_CLIENT_ID")
        self.api_secret = os.getenv("PLANNING_CENTER_SECRET")
        os.makedirs("test_output", exist_ok=True)
        self._request_timestamps = deque()

    def get_group(self, group_name: str) -> GroupsGetResponse:
        url = f"https://api.planningcenteronline.com/groups/v2/groups?where[name]={group_name}"
        response = self._get(url, "test_output/group_response.txt")

        # TODO: Log serialization errors including location
        return GroupsGetResponse.model_validate_json(response.text)

    def get_people(self, group_id: int, offset: int, page_size: int) -> GroupPeopleGetResponse:
        url = f"https://api.planningcenteronline.com/groups/v2/groups/{group_id}/people?offset={offset}&per_page={page_size}"
        response = self._get(url, "test_output/people_response.txt")

        # TODO: Log serialization errors including location
        return GroupPeopleGetResponse.model_validate_json(response.text)

    def get_events(self, group_id: int, earliest_date: str, latest_date: str, offset: int, page_size: int) -> GroupEventsGetResponse:
        url = f"https://api.planningcenteronline.com/groups/v2/groups/{group_id}/events?order=starts_at&filter=not_canceled&where[starts_at][gte]={earliest_date}&where[ends_at][lte]={latest_date}&offset={offset}&per_page={page_size}"
        response = self._get(url, "test_output/event_response.txt")

        # TODO: Log serialization errors including location
        return GroupEventsGetResponse.model_validate_json(response.text)

    def get_attendances(self, event_id: int, offset: int, page_size: int) -> EventAttendancesGetResponse:
        url = f"https://api.planningcenteronline.com/groups/v2/events/{event_id}/attendances?offset={offset}&per_page={page_size}"
        response = self._get(url, "test_output/attendance_response.txt")

        return EventAttendancesGetResponse.model_validate_json(response.text)

    def _get(self, url: str, debug_output_path: str) -> requests.Response:
        while True:
            self._wait_for_rate_limit()
            response = requests.get(url, auth=(self.api_client_id, self.api_secret))
            self._request_timestamps.append(time.monotonic())

            print(f"{response.status_code} {url}")

            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                time.sleep(self.RATE_LIMIT_WINDOW_SECONDS)
                continue

            break

        #TODO: Make this configurable
        with open(debug_output_path, "w") as f:
            f.write(response.text)

        #TODO: Begin returning a Result<success, error> type.
        self._exit_on_http_error(response)

        return response

    def _wait_for_rate_limit(self) -> None:
        now = time.monotonic()
        while self._request_timestamps and now - self._request_timestamps[0] > self.RATE_LIMIT_WINDOW_SECONDS:
            self._request_timestamps.popleft()

        if len(self._request_timestamps) >= self.RATE_LIMIT_MAX_REQUESTS:
            seconds_until_oldest_expires = self.RATE_LIMIT_WINDOW_SECONDS - (now - self._request_timestamps[0])
            if seconds_until_oldest_expires > 0:
                time.sleep(seconds_until_oldest_expires)
            self._request_timestamps.popleft()

    def _exit_on_http_error(self, response: requests.Response) -> None:
        if 400 <= response.status_code <= 599:
            sys.exit(f"Planning Center API request to {response.url} failed with status {response.status_code}: {response.text}")
