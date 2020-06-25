from datetime import datetime
from uuid import UUID

from tests.fixtures.collected_data.schema import (
    CountryOfIncorperation,
    EntityType,
    FullName,
    LinkedProfile,
    Metadata,
    Officer,
    Officers,
    OwnershipStructure,
    PersonalDetails,
    ProfileCategory,
    ProfileCollectedData,
    Role,
    Schema,
    Status,
    Tag,
    Task,
    TaskProgress,
    TaskState,
    TaskType,
    TaskVariant,
)


def get_unmarshalled() -> Schema:
    linked_profile = LinkedProfile(
        id="47c11334-9ffd-11ea-ac63-5a5397e86133",
        category=ProfileCategory.APPLICANT,
        role=Role.INDIVIDUAL_ASSOCIATED,
        tags=[Tag(id=UUID("68ebdf5c-0bbd-11ea-b44e-563aaa5778a5"), is_automatic=False, name="PSC")],
        collected_data=ProfileCollectedData(
            entity_type=EntityType.INDIVIDUAL,
            personal_details=PersonalDetails(
                name=FullName(
                    family_name="Haigh",
                    given_names=["Sebastian", "Thomas"],
                    title=None,
                    alt_family_names=None,
                )
            ),
        ),
        creation_date=datetime(2020, 5, 27, 9, 34, 36),
        display_name="Sebastian Thomas Haigh",
        has_associates=False,
        has_collection_steps=False,
        status=Status.NORMAL,
        task_progress=TaskProgress(completed_count=2, total_count=2),
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
        unresolved_event_types=[],
    )

    return Schema(
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
