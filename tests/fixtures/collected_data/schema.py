from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from jsonmarshal import json_field


class EntityType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"


class CountryOfIncorperation(Enum):
    AFG = "AFG"
    GBR = "GBR"
    JPN = "JPN"
    USA = "USA"


@dataclass
class PreviousName:
    start: date
    end: date
    name: str


@dataclass
class Metadata:
    country_of_incorporation: CountryOfIncorperation
    name: str
    number: str
    previous_names: Optional[List[PreviousName]] = json_field(omitempty=True)


class ProfileCategory(Enum):
    CUSTOMER = "CUSTOMER"
    PREVIOUS_CUSTOMER = "PREVIOUS_CUSTOMER"
    APPLICANT = "APPLICANT"
    INACTIVE_APPLICANT = "INACTIVE_APPLICANT"


class Role(Enum):
    INDIVIDUAL_CUSTOMER = "INDIVIDUAL_CUSTOMER"
    INDIVIDUAL_ASSOCIATED = "INDIVIDUAL_ASSOCIATED"
    COMPANY_CUSTOMER = "COMPANY_CUSTOMER"
    COMPANY_ASSOCIATED = "COMPANY_ASSOCIATED"


@dataclass
class Tag:
    id: UUID
    is_automatic: bool
    name: str


@dataclass
class FullName:
    family_name: str
    given_names: List[str]
    title: Optional[str] = json_field(omitempty=True)
    alt_family_names: Optional[List[str]] = json_field(omitempty=True)


@dataclass
class PersonalDetails:
    name: FullName


@dataclass
class ProfileCollectedData:
    entity_type: EntityType
    personal_details: PersonalDetails


class TaskState(Enum):
    INCOMPLETE = "INCOMPLETE"
    COMPLETED_PASS = "COMPLETED_PASS"
    COMPLETED_FAIL = "COMPLETED_FAIL"


class TaskType(Enum):

    INDIVIDUAL_VERIFY_IDENTITY = "INDIVIDUAL_VERIFY_IDENTITY"
    INDIVIDUAL_VERIFY_ADDRESS = "INDIVIDUAL_VERIFY_ADDRESS"
    INDIVIDUAL_VERIFY_SOURCE_OF_FUNDS = "INDIVIDUAL_VERIFY_SOURCE_OF_FUNDS"
    INDIVIDUAL_ASSESS_MEDIA_AND_POLITICAL_AND_SANCTIONS_EXPOSURE = (
        "INDIVIDUAL_ASSESS_MEDIA_AND_POLITICAL_AND_SANCTIONS_EXPOSURE"
    )
    INDIVIDUAL_ASSESS_POLITICAL_AND_SANCTIONS_EXPOSURE = "INDIVIDUAL_ASSESS_POLITICAL_AND_SANCTIONS_EXPOSURE"
    INDIVIDUAL_ASSESS_POLITICAL_EXPOSURE = "INDIVIDUAL_ASSESS_POLITICAL_EXPOSURE"
    INDIVIDUAL_ASSESS_SANCTIONS_EXPOSURE = "INDIVIDUAL_ASSESS_SANCTIONS_EXPOSURE"
    INDIVIDUAL_VERIFY_BANK_ACCOUNT = "INDIVIDUAL_VERIFY_BANK_ACCOUNT"
    INDIVIDUAL_VERIFY_IMMIGRATION_STATUS = "INDIVIDUAL_VERIFY_IMMIGRATION_STATUS"
    INDIVIDUAL_MANUAL_TASK = "INDIVIDUAL_MANUAL_TASK"
    INDIVIDUAL_ASSESS_DEVICE_REPUTATION = "INDIVIDUAL_ASSESS_DEVICE_REPUTATION"
    INDIVIDUAL_FRAUD_SCREENING = "INDIVIDUAL_FRAUD_SCREENING"
    INDIVIDUAL_VERIFY_TAX_STATUS = "INDIVIDUAL_VERIFY_TAX_STATUS"
    COMPANY_VERIFY_IDENTITY = "COMPANY_VERIFY_IDENTITY"
    COMPANY_VERIFY_ADDRESS = "COMPANY_VERIFY_ADDRESS"
    COMPANY_VERIFY_CHARITY = "COMPANY_VERIFY_CHARITY"
    COMPANY_IDENTIFY_AUTHORIZED_PERSONS = "COMPANY_IDENTIFY_AUTHORIZED_PERSONS"
    COMPANY_IDENTIFY_OFFICERS = "COMPANY_IDENTIFY_OFFICERS"
    COMPANY_IDENTIFY_TRUSTEES = "COMPANY_IDENTIFY_TRUSTEES"
    COMPANY_IDENTIFY_BENEFICIAL_OWNERS = "COMPANY_IDENTIFY_BENEFICIAL_OWNERS"
    COMPANY_REVIEW_FILINGS = "COMPANY_REVIEW_FILINGS"
    COMPANY_ASSESS_SANCTIONS_EXPOSURE = "COMPANY_ASSESS_SANCTIONS_EXPOSURE"
    COMPANY_ASSESS_MEDIA_EXPOSURE = "COMPANY_ASSESS_MEDIA_EXPOSURE"
    COMPANY_ASSESS_MEDIA_AND_SANCTIONS_EXPOSURE = "COMPANY_ASSESS_MEDIA_AND_SANCTIONS_EXPOSURE"
    COMPANY_MANUAL_TASK = "COMPANY_MANUAL_TASK"
    COMPANY_VERIFY_BANK_ACCOUNT = "COMPANY_VERIFY_BANK_ACCOUNT"
    COMPANY_VERIFY_TAX_STATUS = "COMPANY_VERIFY_TAX_STATUS"
    COMPANY_ASSESS_FINANCIALS = "COMPANY_ASSESS_FINANCIALS"
    COMPANY_FRAUD_SCREENING = "COMPANY_FRAUD_SCREENING"
    COMPANY_MERCHANT_FRAUD_SCREENING = "COMPANY_MERCHANT_FRAUD_SCREENING"


@dataclass
class TaskVariant:
    id: UUID
    task_type: TaskType
    alias: str
    description: Optional[str] = json_field(omitempty=True)
    name: Optional[str] = json_field(omitempty=True)


@dataclass
class Task:
    creation_date: datetime
    id: UUID
    is_complete: bool
    is_expired: bool
    is_skipped: bool
    state: TaskState
    type: TaskType
    variant: TaskVariant


class UnresolvedEventType(Enum):
    PEP_FLAG = "PEP_FLAG"
    SANCTION_FLAG = "SANCTION_FLAG"
    DOCUMENT_EXPIRY = "DOCUMENT_EXPIRY"
    TRANSACTION_ALERT = "TRANSACTION_ALERT"
    REVIEW_NEEDED = "REVIEW_NEEDED"
    ADVERSE_MEDIA_FLAG = "ADVERSE_MEDIA_FLAG"
    REFER_FLAG = "REFER_FLAG"
    CHECK_EXPIRY = "CHECK_EXPIRY"
    FRAUD_FLAG = "FRAUD_FLAG"


@dataclass
class TaskProgress:
    completed_count: int
    total_count: int


class Status(Enum):
    NORMAL = "NORMAL"


@dataclass
class LinkedProfile:
    category: ProfileCategory
    collected_data: ProfileCollectedData
    creation_date: datetime
    display_name: str
    has_associates: bool
    has_collection_steps: bool
    id: str
    role: Role
    status: Status
    tags: List[Tag]
    task_progress: TaskProgress
    tasks: List[Task]
    unresolved_event_types: List[UnresolvedEventType]


@dataclass
class Shareholding:
    amount: int
    currency: str
    percentage: float
    provider_name: str
    share_class: str


@dataclass
class Officer:
    entity_type: EntityType
    linked_profile: LinkedProfile
    merged_resolver_ids: List[UUID] = json_field(omitempty=True)
    resolver_id: UUID = json_field(omitempty=True)
    task_variant_ids: List[UUID] = json_field(omitempty=True)
    unverified_task_variant_ids: List[UUID] = json_field(omitempty=True)
    natures_of_control: Optional[List[str]] = json_field(omitempty=True)
    shareholdings: Optional[List[Shareholding]] = json_field(omitempty=True)


@dataclass
class Officers:
    directors: Optional[List[Officer]] = json_field(omitempty=True)
    other: Optional[List[Officer]] = json_field(omitempty=True)
    partners: Optional[List[Officer]] = json_field(omitempty=True)
    resigned: Optional[List[Officer]] = json_field(omitempty=True)
    secretaries: Optional[List[Officer]] = json_field(omitempty=True)
    trustees: Optional[List[Officer]] = json_field(omitempty=True)


@dataclass
class ShareClass:
    name: str
    currency: str
    value: int
    votes: int


@dataclass
class OwnershipStructure:
    beneficial_owners: List[Officer]
    share_classes: Optional[List[ShareClass]] = json_field(omitempty=True)


@dataclass
class Schema:
    entity_type: EntityType
    metadata: Metadata
    officers: Officers
    ownership_structure: OwnershipStructure
