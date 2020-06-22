from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID


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
    previous_names: Optional[List[PreviousName]]


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
    title: Optional[str]
    alt_family_names: Optional[List[str]]


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
    description: Optional[str]
    name: Optional[str]


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


@dataclass
class LinkedProfile:
    id: str
    category: ProfileCategory
    role: Role
    tags: List[Tag]
    collected_data: ProfileCollectedData
    tasks: List[Task]


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
    merged_resolver_ids: List[UUID]
    resolver_id: UUID
    task_variant_ids: List[UUID]
    unverified_task_variant_ids: List[UUID]
    natures_of_control: Optional[List[str]]
    shareholdings: Optional[List[Shareholding]]


@dataclass
class Officers:
    directors: Optional[List[Officer]]
    other: Optional[List[Officer]]
    partners: Optional[List[Officer]]
    resigned: Optional[List[Officer]]
    secretaries: Optional[List[Officer]]
    trustees: Optional[List[Officer]]


@dataclass
class ShareClass:
    name: str
    currency: str
    value: int
    votes: int


@dataclass
class OwnershipStructure:
    beneficial_owners: List[Officer]
    share_classes: Optional[List[ShareClass]]


@dataclass
class CollectedData:
    entity_type: EntityType
    metadata: Metadata
    officers: Officers
    ownership_structure: OwnershipStructure


linked_profile = LinkedProfile(
    id="47c11334-9ffd-11ea-ac63-5a5397e86133",
    category=ProfileCategory.APPLICANT,
    role=Role.INDIVIDUAL_ASSOCIATED,
    tags=[Tag(id=UUID("68ebdf5c-0bbd-11ea-b44e-563aaa5778a5"), is_automatic=False, name="PSC")],
    collected_data=ProfileCollectedData(
        entity_type=EntityType.INDIVIDUAL,
        personal_details=PersonalDetails(
            name=FullName(
                family_name="Haigh", given_names=["Sebastian", "Thomas"], title=None, alt_family_names=None
            )
        ),
    ),
    tasks=[
        Task(
            creation_date=datetime(2020, 5, 27, 9, 34, 36),
            id=UUID("47e42692-9ffd-11ea-8f2a-5a5397e86133"),
            is_complete=True,
            is_expired=False,
            is_skipped=False,
            state=TaskState.COMPLETED_PASS,
            type=TaskType.INDIVIDUAL_ASSESS_POLITICAL_AND_SANCTIONS_EXPOSURE,
            variant=TaskVariant(
                alias="individual_assess_political_and_sanctions_exposuredefault",
                id=UUID("990b6728-8e7e-11e8-baed-0a580a000380"),
                task_type=TaskType.INDIVIDUAL_ASSESS_POLITICAL_AND_SANCTIONS_EXPOSURE,
                description=None,
                name=None,
            ),
        ),
        Task(
            creation_date=datetime(2020, 5, 27, 9, 34, 37),
            id=UUID("47eba42e-9ffd-11ea-a080-5a5397e86133"),
            is_complete=True,
            is_expired=False,
            is_skipped=False,
            state=TaskState.COMPLETED_PASS,
            type=TaskType.INDIVIDUAL_FRAUD_SCREENING,
            variant=TaskVariant(
                alias="individual_fraud_screeningdefault",
                id=UUID("ca3680a4-5713-11ea-894c-22bc58dfbf7d"),
                task_type=TaskType.INDIVIDUAL_FRAUD_SCREENING,
                description=None,
                name=None,
            ),
        ),
    ],
)


expected = CollectedData(
    entity_type=EntityType.COMPANY,
    metadata=Metadata(
        country_of_incorporation=CountryOfIncorperation.GBR,
        name="Amazon Ltd",
        number="10804351",
        previous_names=None,
    ),
    officers=Officers(
        directors=[
            Officer(
                entity_type=EntityType.INDIVIDUAL,
                linked_profile=linked_profile,
                merged_resolver_ids=[],
                resolver_id=UUID("59a7749e-9ffd-11ea-8c58-56fdcde0987e"),
                task_variant_ids=[UUID("fda0a2b6-d7aa-11e8-8298-0a580a00031c")],
                unverified_task_variant_ids=[],
                natures_of_control=None,
                shareholdings=None,
            )
        ],
        other=None,
        partners=None,
        resigned=None,
        secretaries=None,
        trustees=None,
    ),
    ownership_structure=OwnershipStructure(
        beneficial_owners=[
            Officer(
                entity_type=EntityType.INDIVIDUAL,
                linked_profile=linked_profile,
                merged_resolver_ids=[],
                resolver_id=UUID("59a7c354-9ffd-11ea-be4d-56fdcde0987e"),
                task_variant_ids=[
                    UUID("1098df9e-d7ab-11e8-990d-0a580a000562"),
                    UUID("fda0a2b6-d7aa-11e8-8298-0a580a00031c"),
                ],
                unverified_task_variant_ids=[],
                natures_of_control=[],
                shareholdings=[],
            )
        ],
        share_classes=None,
    ),
)
