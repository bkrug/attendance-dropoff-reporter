from datetime import datetime, timezone
from planning_center_models import GroupPeopleGetResponse
from planning_center_models.people import PersonDatum, PersonAttributes
from planning_center_models.common import DatumLinks, ResponseLinks
from .meta_builder import MetaBuilder

class GroupPeopleGetResponseBuilder:
    def __init__(self):
        self._people: list[PersonDatum] = []
        self._meta_builder = MetaBuilder(parent_id=1, parent_type="Group")

    def add_person(self, person_id: int, first_name: str, last_name: str) -> "GroupPeopleGetResponseBuilder":
        self._people.append(
            PersonDatum(
                type="Person",
                id=person_id,
                attributes=PersonAttributes(
                    addresses=[],
                    avatar_url="",
                    created_at=datetime.now(timezone.utc),
                    email_addresses=[],
                    first_name=first_name,
                    gender=None,
                    last_name=last_name,
                    permissions="",
                    phone_numbers=[],
                ),
                links=DatumLinks(),
            )
        )
        return self

    def with_next(self, next_offset: int, total_count: int) -> "GroupPeopleGetResponseBuilder":
        self._meta_builder.with_next(next_offset, total_count)
        return self

    def build(self) -> GroupPeopleGetResponse:
        return GroupPeopleGetResponse(
            links=ResponseLinks(links_self="https://api.planningcenteronline.com/groups/v2/groups/1/people"),
            data=list(self._people),
            included=[],
            meta=self._meta_builder.with_count(len(self._people)).build(),
        )
