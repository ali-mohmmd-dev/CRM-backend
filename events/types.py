from typing import NotRequired, TypedDict


class EventNames:
    LEAD_CALLED = 'LeadCalled'
    LEAD_CONVERTED = 'LeadConverted'
    CUSTOMER_FOLLOWED_UP = 'CustomerFollowedUp'
    WORK_CREATED = 'WorkCreated'
    WORK_ASSIGNED = 'WorkAssigned'
    WORK_STATUS_CHANGED = 'WorkStatusChanged'


class LeadCalledPayload(TypedDict):
    lead_id: int
    organization_id: int
    status: str
    called_at: str


class LeadConvertedPayload(TypedDict):
    lead_id: int
    organization_id: int
    name: str
    company: str
    email: str
    phone: str
    notes: str
    last_contact: str


class CustomerFollowedUpPayload(TypedDict):
    customer_id: int
    organization_id: int
    last_contact: str


class WorkCreatedPayload(TypedDict):
    work_id: int
    organization_id: int
    title: str
    status: str
    assigned_to_id: NotRequired[int | None]


class WorkAssignedPayload(TypedDict):
    work_id: int
    organization_id: int
    assigned_to_id: int | None
    previous_assigned_to_id: int | None


class WorkStatusChangedPayload(TypedDict):
    work_id: int
    organization_id: int
    status: str
    previous_status: str
