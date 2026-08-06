from planning_center_models.common import Meta, Next, Parent

class MetaBuilder:
    def __init__(self, parent_id: int, parent_type: str):
        self._parent_id = parent_id
        self._parent_type = parent_type
        self._count = 0
        self._total_count: int | None = None
        self._next_offset: int | None = None

    def with_count(self, count: int) -> "MetaBuilder":
        self._count = count
        return self

    def with_next(self, next_offset: int, total_count: int) -> "MetaBuilder":
        self._next_offset = next_offset
        self._total_count = total_count
        return self

    def build(self) -> Meta:
        return Meta(
            total_count=self._total_count if self._total_count is not None else self._count,
            count=self._count,
            next=Next(offset=self._next_offset) if self._next_offset is not None else None,
            can_order_by=[],
            can_query_by=[],
            parent=Parent(id=self._parent_id, type=self._parent_type),
        )
