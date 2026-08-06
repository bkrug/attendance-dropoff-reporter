from typing import List, Any
from datetime import datetime


class EmailAddress:
    address: str
    location: str
    primary: bool

    def __init__(self, address: str, location: str, primary: bool) -> None:
        self.address = address
        self.location = location
        self.primary = primary


class PhoneNumber:
    number: str
    carrier: None
    location: str
    primary: bool

    def __init__(self, number: str, carrier: None, location: str, primary: bool) -> None:
        self.number = number
        self.carrier = carrier
        self.location = location
        self.primary = primary


class PersonAttributes:
    addresses: List[Any]
    avatar_url: str
    created_at: datetime
    email_addresses: List[EmailAddress]
    first_name: str
    gender: str
    last_name: str
    permissions: str
    phone_numbers: List[PhoneNumber]

    def __init__(self, addresses: List[Any], avatar_url: str, created_at: datetime, email_addresses: List[EmailAddress], first_name: str, gender: str, last_name: str, permissions: str, phone_numbers: List[PhoneNumber]) -> None:
        self.addresses = addresses
        self.avatar_url = avatar_url
        self.created_at = created_at
        self.email_addresses = email_addresses
        self.first_name = first_name
        self.gender = gender
        self.last_name = last_name
        self.permissions = permissions
        self.phone_numbers = phone_numbers


class DatumLinks:
    links_self: str
    html: str

    def __init__(self, links_self: str, html: str) -> None:
        self.links_self = links_self
        self.html = html


class PersonDatum:
    type: str
    id: int
    attributes: PersonAttributes
    links: DatumLinks

    def __init__(self, type: str, id: int, attributes: PersonAttributes, links: DatumLinks) -> None:
        self.type = type
        self.id = id
        self.attributes = attributes
        self.links = links


class ResponseLinks:
    links_self: str
    next: str

    def __init__(self, links_self: str, next: str) -> None:
        self.links_self = links_self
        self.next = next


class Next:
    offset: int

    def __init__(self, offset: int) -> None:
        self.offset = offset


class Parent:
    id: int
    type: str

    def __init__(self, id: int, type: str) -> None:
        self.id = id
        self.type = type


class Meta:
    total_count: int
    count: int
    next: Next
    can_order_by: List[str]
    can_query_by: List[str]
    parent: Parent

    def __init__(self, total_count: int, count: int, next: Next, can_order_by: List[str], can_query_by: List[str], parent: Parent) -> None:
        self.total_count = total_count
        self.count = count
        self.next = next
        self.can_order_by = can_order_by
        self.can_query_by = can_query_by
        self.parent = parent


class GroupPeopleGetResponse:
    links: ResponseLinks
    data: List[PersonDatum]
    included: List[Any]
    meta: Meta

    def __init__(self, links: ResponseLinks, data: List[PersonDatum], included: List[Any], meta: Meta) -> None:
        self.links = links
        self.data = data
        self.included = included
        self.meta = meta
