# content of test_sysexit.py
import pytest
from src.planning_center_client import PlanningCenterClient
from src.planning_center_models import GroupsGetResponse
from src.planning_center_models.common import Meta, Parent, ResponseLinks
from .groups_get_response_builder import GroupsGetResponseBuilder

class FakePlanningCenterClient(PlanningCenterClient):
    def __init__(self):
        pass

    def get_group(self, group_name: str) -> GroupsGetResponse:
        return GroupsGetResponse(
            links=ResponseLinks(links_self="https://api.planningcenteronline.com/groups/v2/groups"),
            data=[],
            included=[],
            meta=Meta(
                total_count=0,
                count=0,
                can_order_by=[],
                can_query_by=[],
                parent=Parent(id=522735, type="Organization"),
            ),
        )

# content of test_class.py
class ReportTests:
    def reportTests_groupDoesNotExist_ExpectErrorMsg(self):
        emptyGroupResponse = GroupsGetResponseBuilder().build()
        x = "this"
        assert "h" in x

    def reportTests_groupExistsWithNoEvents_ExpectErrorMsg(self):
        groupResponse = GroupsGetResponseBuilder().add_group(1, "St. James Attendance").build()
        x = "this"
        assert "h" in x
