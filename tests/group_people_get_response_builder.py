from planning_center_models import GroupPeopleGetResponse
from planning_center_models.common import ResponseLinks, Meta, Parent

class GroupPeopleGetResponseBuilder:
    def build(self) -> GroupPeopleGetResponse:
        return GroupPeopleGetResponse(
            links=ResponseLinks(links_self="https://api.planningcenteronline.com/groups/v2/groups/1/people"),
            data=[],
            included=[],
            meta=Meta(
                total_count=0,
                count=0,
                can_order_by=[],
                can_query_by=[],
                parent=Parent(id=1, type="Group"),
            ),
        )
