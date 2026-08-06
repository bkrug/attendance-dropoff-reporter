from datetime import datetime, timezone
from planning_center_models import GroupsGetResponse
from planning_center_models.groups import GroupDatum, GroupAttributes, GroupImage, GroupRelationships
from planning_center_models.common import DatumLinks, ResponseLinks, Relationship
from .meta_builder import MetaBuilder

class GroupsGetResponseBuilder:
    def __init__(self):
        self._groups: list[GroupDatum] = []
        self._meta_builder = MetaBuilder(parent_id=522735, parent_type="Organization")

    def add_group(self, group_id: int, group_name: str) -> "GroupsGetResponseBuilder":
        self._groups.append(
            GroupDatum(
                type="Group",
                id=group_id,
                attributes=GroupAttributes(
                    archived_at=None,
                    chat_enabled=False,
                    contact_email=None,
                    created_at=datetime.now(timezone.utc),
                    description=None,
                    description_as_plain_text=None,
                    direct_messages_enabled=False,
                    events_listed=False,
                    events_visibility="members",
                    header_image=GroupImage(thumbnail=None, medium=None, original=None),
                    leaders_can_search_people_database=False,
                    listed=False,
                    location_type_preference="physical",
                    members_are_confidential=False,
                    memberships_count=0,
                    name=group_name,
                    public_church_center_web_url=None,
                    schedule=None,
                    virtual_location_url=None,
                ),
                relationships=GroupRelationships(
                    group_type=Relationship(data=None),
                    location=Relationship(data=None),
                ),
                links=DatumLinks(),
            )
        )
        return self

    def with_next(self, next_offset: int, total_count: int) -> "GroupsGetResponseBuilder":
        self._meta_builder.with_next(next_offset, total_count)
        return self

    def build(self) -> GroupsGetResponse:
        return GroupsGetResponse(
            links=ResponseLinks(links_self="https://api.planningcenteronline.com/groups/v2/groups"),
            data=list(self._groups),
            included=[],
            meta=self._meta_builder.with_count(len(self._groups)).build(),
        )
