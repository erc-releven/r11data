"""Pydantic models for main table to RDF conversion."""

from typing import Annotated, Any, Literal as TypingLiteral, Self

from pydantic import (
    AfterValidator,
    AnyUrl,
    BaseModel,
    BeforeValidator,
    Field,
    model_validator,
)
from pydantic_extra_types.coordinate import Coordinate


class Person(BaseModel):
    """Person model corresponding to the main 'Persons' sheet."""

    identifier: str = Field(validation_alias="Identifier", coerce_numbers_to_str=True)
    service: Annotated[
        str,
        Field(validation_alias="Service"),
        BeforeValidator(lambda x: "https://r11.eu/" if x is None else x),
    ]
    descriptive_name: str = Field(validation_alias="Descriptive name")
    id_string: str = Field(validation_alias="ID string")

    # optional fields
    wisski_id: Annotated[
        AnyUrl | None, AfterValidator(lambda x: str(x) if x is not None else x)
    ] = Field(validation_alias="WissKI ID")

    name_in_sources_orig: str | None = Field(validation_alias="Name in source (orig)")
    name_in_sources_transl: str | None = Field(
        validation_alias="Name in source (transl)"
    )
    gender_assignment: TypingLiteral["Male", "Female", "Eunuch"] | None = Field(
        validation_alias="Gender assignment"
    )
    ethnicity: str | None = Field(validation_alias="Ethnicity")
    social_role: str | None = Field(validation_alias="Social role (C2)")
    legal_role: str | None = Field(validation_alias="Legal role (C12)")
    language_skill: str | None = Field(validation_alias="Language skill")
    religion: str | None = Field(validation_alias="Religion")
    authority: str | None = Field(validation_alias="Authority")
    authority_group: str | None = Field(validation_alias="Authority group")
    based_on: str | None = Field(validation_alias="Based on")
    source_text_publication: str | None = Field(
        validation_alias="Source text/publication"
    )
    source_text_reference: str | None = Field(validation_alias="Source text/reference")
    source_text_excerpt: str | None = Field(validation_alias="Source text/excerpt")

    @model_validator(mode="before")
    @classmethod
    def _get_descriptive_name(cls, data: Any) -> Any:
        if data.get("Descriptive name") is None:
            data["Descriptive name"] = data["Identifier"]
        return data

    @model_validator(mode="after")
    def _check_publication_reference_mutual_dependent(self) -> Self:
        if (self.source_text_publication is None) != (
            self.source_text_reference is None
        ):
            raise ValueError(
                "Text Publication and Text Reference fields are mutually dependent."
            )
        return self

    @model_validator(mode="after")
    def _check_authority_authority_group_mutual_exclusive(self) -> Self:
        if self.authority and self.authority_group:
            raise ValueError(
                "Authority and Authority Group fields are mutually exclusive."
            )
        return self


class Place(BaseModel):
    """Place model corresponding to the main 'Places' sheet."""

    reference_name: str = Field(validation_alias="Reference name")

    pleiades_id: AnyUrl | None = Field(validation_alias="Pleiades ID")
    geonames_id: AnyUrl | None = Field(validation_alias="Geonames ID")
    wikidata_id: AnyUrl | None = Field(validation_alias="Wikidata ID")
    location_coordinates: Coordinate | None = Field(
        validation_alias="Location coordinates"
    )
    place_type: str | None = Field(validation_alias="Place type")
    earliest_existence: str | None = Field(validation_alias="Earliest existence")
    latest_existence: str | None = Field(validation_alias="Latest existence")
    succeeds_place: str | None = Field(validation_alias="Succeeds place")
    incorporates_place: str | None = Field(validation_alias="Incorporates place")
    had_population_group: str | None = Field(validation_alias="Had population group")
    authority: str | None = Field(validation_alias="Authority")
    authority_group: str | None = Field(validation_alias="Authority group")
    based_on: str | None = Field(validation_alias="Based on")
    source_text_publication: str | None = Field(
        validation_alias="Source text/publication"
    )
    source_text_excerpt: str | None = Field(validation_alias="Source text/excerpt")


class AuthorGroup(BaseModel):
    """AuthorGroup model corresponding to the main 'Author groups' sheet."""

    wisski_id: AnyUrl | None = Field(validation_alias="WissKI ID")

    group_identifier: str = Field(validation_alias="Group identifier")
    group_member: str = Field(validation_alias="Group member")

    group_member_id: str | None = Field(
        init=False, default=None, description="Computed from validator"
    )
    group_member_label: str | None = Field(
        init=False, default=None, description="Computed from validator"
    )

    @model_validator(mode="after")
    def _compute_group_member_fields(self):
        self.group_member_id, self.group_member_label = map(
            str.strip, self.group_member.split(" / ")
        )

        return self


class ActorGroup(BaseModel):
    """ActorGroup model corresponding to the main 'Actor Group' sheet."""

    group_identifier: str = Field(validation_alias="Group identifier")
    group_member: str = Field(validation_alias="Group member")
    authority: str = Field(validation_alias="Authority")
    authority_group: str | None = Field(validation_alias="Authority group")
    based_on: str | None = Field(validation_alias="Based on")
    source_text_publication: str = Field(validation_alias="Source text/publication")
    source_text_reference: str = Field(validation_alias="Source text/reference")
    source_text_excerpt: str | None = Field(validation_alias="Source text/excerpt")


class TextPublication(BaseModel):
    """TextPublication model corresponding to the main 'Text publications' sheet."""

    text_identifier: str = Field(validation_alias="Text identifier")

    text_name: str | None = Field(validation_alias="Text name")
    creation_date: str | None = Field(validation_alias="Creation date")
    author: str | None = Field(validation_alias="Author")
    author_group: str | None = Field(validation_alias="Author group")
    edition: str | None = Field(validation_alias="Edition")
    editor: str | None = Field(validation_alias="Editor")
    editor_group: str | None = Field(validation_alias="Editor group")
    authority: str | None = Field(validation_alias="Authority")
    authority_group: str | None = Field(validation_alias="Authority group")

    source_text_publication: str | None = Field(
        validation_alias="Source text/publication"
    )
    source_text_reference: str | None = Field(validation_alias="Source text/reference")
    source_text_excerpt: str | None = Field(validation_alias="Source text/excerpt")
