import requests
import os
import time
import logging
from collections import deque
from http import HTTPStatus
from result import Err, Ok, Result
from planning_center_models import GroupPeopleGetResponse, GroupEventsGetResponse, EventAttendancesGetResponse, GroupsGetResponse

class PlanningCenterClient:
    def __init__(self):
        # TODO: Raise an error if either of these values is blank
        self.api_client_id = os.getenv("PLANNING_CENTER_CLIENT_ID")
        self.api_secret = os.getenv("PLANNING_CENTER_SECRET")
        self.rate_limit_max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "80"))
        self.rate_limit_window_seconds = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "20"))
        self.log_response_text = os.getenv("LOG_RESPONSE_TEXT", "").lower()=="true" or os.getenv("LOG_RESPONSE_TEXT", "")=="1"
        os.makedirs("test_output", exist_ok=True)
        self._request_timestamps = deque()

    def get_group(self, group_name: str) -> Result[GroupsGetResponse, str]:
        url = f"https://api.planningcenteronline.com/groups/v2/groups?where[name]={group_name}"

        # TODO: Log serialization errors including location
        return self._get(url, "test_output/group_response.txt").map(
            lambda response: GroupsGetResponse.model_validate_json(response.text)
        )

    def get_people(self, group_id: int, offset: int, page_size: int) -> Result[GroupPeopleGetResponse, str]:
        url = f"https://api.planningcenteronline.com/groups/v2/groups/{group_id}/people?offset={offset}&per_page={page_size}"

        # TODO: Log serialization errors including location
        return self._get(url, "test_output/people_response.txt").map(
            lambda response: GroupPeopleGetResponse.model_validate_json(response.text)
        )

    def get_events(self, group_id: int, earliest_date: str, latest_date: str, offset: int, page_size: int) -> Result[GroupEventsGetResponse, str]:
        url = f"https://api.planningcenteronline.com/groups/v2/groups/{group_id}/events?order=starts_at&filter=not_canceled&where[starts_at][gte]={earliest_date}&where[ends_at][lte]={latest_date}&offset={offset}&per_page={page_size}"

        # TODO: Log serialization errors including location
        return self._get(url, "test_output/event_response.txt").map(
            lambda response: GroupEventsGetResponse.model_validate_json(response.text)
        )

    def get_attendances(self, event_id: int, offset: int, page_size: int) -> Result[EventAttendancesGetResponse, str]:
        url = f"https://api.planningcenteronline.com/groups/v2/events/{event_id}/attendances?offset={offset}&per_page={page_size}"

        return self._get(url, "test_output/attendance_response.txt").map(
            lambda response: EventAttendancesGetResponse.model_validate_json(response.text)
        )

    def _get(self, url: str, debug_output_path: str) -> Result[requests.Response, str]:
        while True:
            self._wait_for_rate_limit()
            response = requests.get(url, auth=(self.api_client_id, self.api_secret))
            self._request_timestamps.append(time.monotonic())

            logging.info(f"{response.status_code} {url}")

            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                time.sleep(self.rate_limit_window_seconds)
                continue

            break

        if self.log_response_text:
            with open(debug_output_path, "w") as f:
                f.write(response.text)

        if 400 <= response.status_code <= 599:
            logging.error(f"{response.status_code} {response.text}")
            return Err("Failure to communicate with Planning Center")

        return Ok(response)

    def _wait_for_rate_limit(self) -> None:
        now = time.monotonic()
        while self._request_timestamps and now - self._request_timestamps[0] > self.rate_limit_window_seconds:
            self._request_timestamps.popleft()

        if len(self._request_timestamps) >= self.rate_limit_max_requests:
            seconds_until_oldest_expires = self.rate_limit_window_seconds - (now - self._request_timestamps[0])
            if seconds_until_oldest_expires > 0:
                time.sleep(seconds_until_oldest_expires)
            self._request_timestamps.popleft()
