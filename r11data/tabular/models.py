"""Pydantic models for main table to RDF conversion."""

from typing import Annotated, Any, Self
from typing import Literal as TypingLiteral

from pydantic import (
    AfterValidator,
    AliasChoices,
    AnyUrl,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)
from pydantic_extra_types.coordinate import Coordinate
from r11data.tabular.utils.rdf_utils import aaao, crm, lrm, mkuri, pwro, r11spec
from rdflib import URIRef


class _AuthoritySourceBase(BaseModel):
    """Base model for Authority/Text data.

    The fields and validators defined in this base model
    are common across several sheets and ergo can be generalized.
    """

    model_config = ConfigDict(str_strip_whitespace=True, arbitrary_types_allowed=True)

    authority: str | None = Field(validation_alias="Authority")
    authority_group: str | None = Field(validation_alias="Authority group")

    @model_validator(mode="after")
    def _check_authority_authority_group_mutual_exclusive(self) -> Self:
        if self.authority and self.authority_group:
            raise ValueError(
                "Authority and Authority Group fields are mutually exclusive."
            )
        return self

    based_on: str | None = Field(validation_alias="Based on")

    source_text_publication: str | None = Field(
        validation_alias="Source text/publication"
    )
    source_text_reference: str | None = Field(validation_alias="Source text/reference")
    source_text_excerpt: str | None = Field(validation_alias="Source text/excerpt")

    # note: this urgently needs to be reflected in the triple generators
    @model_validator(mode="after")
    def _check_publication_reference_dependency(self) -> Self:
        if (
            self.source_text_reference is not None
            and self.source_text_publication is None
        ):
            raise ValueError("Text Reference without Text Publication not allowed.")
        return self

    @model_validator(mode="after")
    def _check_reference_excerpt_dependency(self) -> Self:
        if self.source_text_excerpt is not None and self.source_text_reference is None:
            raise ValueError("Text Excerpt without Text Reference not allowed.")
        return self

    @computed_field
    @property
    def publication_uri(self) -> URIRef | None:
        if (publication := self.source_text_publication) is None:
            return None

        return mkuri(publication, "https://r11.eu/")

    @computed_field
    @property
    def passage_uri(self) -> URIRef | None:
        publication_uri = self.publication_uri
        reference = self.source_text_reference
        excerpt = self.source_text_excerpt

        if publication_uri is None:
            return

        hash_values = [
            value
            for value in (publication_uri, reference, excerpt)
            if value is not None
        ]

        return mkuri(*hash_values)


class Person(_AuthoritySourceBase):
    """Person model corresponding to the main 'Persons' sheet."""

    model_config = ConfigDict(arbitrary_types_allowed=True)  # mainly for person_uri

    identifier: str = Field(validation_alias="Identifier", coerce_numbers_to_str=True)
    service: Annotated[
        str,
        Field(validation_alias="Service"),
        BeforeValidator(lambda x: "https://r11.eu/" if x is None else x),
    ]
    descriptive_name: str = Field(validation_alias="Descriptive name")
    id_string: str = Field(validation_alias="ID string")

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

    @computed_field
    @property
    def person_uri(self) -> URIRef:
        return mkuri(self.identifier, self.service)

    @model_validator(mode="before")
    @classmethod
    def _get_descriptive_name(cls, data: Any) -> Any:
        if data.get("Descriptive name") is None:
            data["Descriptive name"] = data["Identifier"]
        return data


class Place(_AuthoritySourceBase):
    """Place model corresponding to the main 'Places' sheet."""

    reference_name: str = Field(validation_alias="Reference name")

    @computed_field
    @property
    def place_uri(self) -> URIRef:
        return mkuri(self.reference_name, self.service)

    @computed_field
    @property
    def service(self) -> URIRef:
        return (
            URIRef("https://pbw2016.kdl.kcl.ac.uk/")
            if self.authority == "44335536 / Roueché, Charlotte"
            else URIRef("https://r11.eu/")
        )

    pleiades_id: Annotated[
        AnyUrl | None, AfterValidator(lambda x: str(x) if x is not None else x)
    ] = Field(validation_alias="Pleiades ID")

    geonames_id: Annotated[
        AnyUrl | None, AfterValidator(lambda x: str(x) if x is not None else x)
    ] = Field(validation_alias="Geonames ID")

    wikidata_id: Annotated[
        AnyUrl | None, AfterValidator(lambda x: str(x) if x is not None else x)
    ] = Field(validation_alias="Wikidata ID")

    location_coordinates: Coordinate | None = Field(
        validation_alias="Location coordinates"
    )
    place_type: str | None = Field(validation_alias="Place type")
    earliest_existence: str | None = Field(validation_alias="Earliest existence")
    latest_existence: str | None = Field(validation_alias="Latest existence")
    succeeds_place: str | None = Field(validation_alias="Succeeds place")
    incorporates_place: str | None = Field(validation_alias="Incorporates place")
    had_population_group: str | None = Field(validation_alias="Had population group")


class AuthorGroup(BaseModel):
    """AuthorGroup model corresponding to the main 'Author groups' sheet."""

    model_config = ConfigDict(str_strip_whitespace=True, arbitrary_types_allowed=True)

    wisski_id: Annotated[
        AnyUrl | None, AfterValidator(lambda x: str(x) if x is not None else x)
    ] = Field(validation_alias="WissKI ID")

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

    @computed_field
    @property
    def group_uri(self) -> URIRef:
        return mkuri(self.group_identifier, "https://r11.eu/")


class ActorGroup(_AuthoritySourceBase):
    """ActorGroup model corresponding to the main 'Actor Group' sheet."""

    group_identifier: str = Field(validation_alias="Group identifier")
    # optional only for Marton
    group_member: str | None = Field(validation_alias="Group member")

    @computed_field
    @property
    def group_uri(self) -> URIRef:
        return mkuri(self.group_identifier, "https://r11.eu/")


class TextPublication(_AuthoritySourceBase):
    """TextPublication model corresponding to the main 'Text publications' sheet."""

    @computed_field
    @property
    def text_expression_uri(self) -> URIRef:
        passage_uri = self.passage_uri
        assert passage_uri is not None

        return passage_uri

    @computed_field
    @property
    def text_expression_creation_uri(self) -> URIRef:
        return mkuri(lrm.F28_Expression_Creation, self.text_expression_uri)

    @computed_field
    @property
    def text_expression_appellation_uri(self) -> URIRef:
        return mkuri(crm.E33_E41_Linguistic_Appellation, self.text_expression_uri)

    @computed_field
    @property
    def text_publication_uri(self) -> URIRef:
        publication_uri = self.publication_uri
        assert publication_uri is not None

        return publication_uri

    @computed_field
    @property
    def text_publication_creation_uri(self) -> URIRef:
        return mkuri(lrm.F28_Expression_Creation, self.text_publication_uri)

    text_identifier: str = Field(validation_alias="Text identifier")

    text_name: str | None = Field(validation_alias="Text name")
    creation_date: str | None = Field(validation_alias="Creation date")
    author: str | None = Field(validation_alias="Author")
    author_group: str | None = Field(validation_alias="Author group")

    edition: str = Field(validation_alias="Edition")

    editor: str | None = Field(validation_alias="Editor")
    editor_group: str | None = Field(validation_alias="Editor group")

    based_on: str | None = Field(
        default=None, exclude=True
    )  # overwrite; based_on not in TP sheet


class Manuscript(_AuthoritySourceBase):
    @computed_field
    @property
    def manuscript_uri(self) -> URIRef:
        return mkuri(r11spec.Manuscript, self.identifier)

    @computed_field
    @property
    def manuscript_production_uri(self) -> URIRef:
        return mkuri(crm.E12_Production, self.identifier)

    identifier: str = Field(validation_alias="Identifier")
    dating: str = Field(validation_alias="Dating")
    place_copied: str | None = Field(validation_alias="Place copied")
    contains_text: str = Field(validation_alias="Contains text")
    scribe: str = Field(validation_alias="Scribe")
    commissioned_by: str | None = Field(validation_alias="Commissioned by")


class SocialRelationship(_AuthoritySourceBase):
    main_person: str = Field(validation_alias="Main person")
    related_person: str = Field(validation_alias="Related person")
    relationship_type: Annotated[
        str,
        Field(validation_alias="Relationship type"),
    ]

    start_date: str | None = Field(validation_alias="Start date")
    end_date: str | None = Field(validation_alias="End date")


class Journey(_AuthoritySourceBase):
    journey_id: str | None = Field(validation_alias="Journey id")

    who_travelled: str | None = Field(validation_alias="Who travelled")
    group_travelled: str | None = Field(validation_alias="Group travelled")

    journey_type: str | None = Field(validation_alias="Journey type")

    sent_by_person: str | None = Field(validation_alias="Sent by person")

    visited_person: str | None = Field(validation_alias="Visited person")
    visited_place: str | None = Field(validation_alias="Visited place")
    visited_when: str | None = Field(validation_alias="Visited when")

    des_origin: str | None = Field(validation_alias="Des. Origin")
    des_destination: str | None = Field(validation_alias="Des. Destination")
    real_origin: str | None = Field(validation_alias="Real Origin")
    real_destination: str | None = Field(validation_alias="Real Dest.")

    start_date: str | None = Field(validation_alias="Start date")
    end_date: str | None = Field(validation_alias="End date")

    @model_validator(mode="after")
    def _check_traveller(self) -> Self:
        if not (self.who_travelled or self.group_travelled):
            msg = "Travelling party required. Expected either 'who_travelled' or 'group_travelled'."
            raise ValueError(msg)
        return self


class GeopoliticalEvent(_AuthoritySourceBase):
    event_label: str = Field(validation_alias="Event label")
    event_date: str = Field(validation_alias="Event date")
    event_type: str = Field(validation_alias="Event type")

    involved_person: str | None = Field(validation_alias="Involved person")

    created_place: str | None = Field(validation_alias="Created place")
    destroyed_place: str | None = Field(validation_alias="Destroyed place")

    challenge: str | None = Field(validation_alias="Challenge to authority status")

    intended_target_place: str | None = Field(
        validation_alias="Intended target place of attack"
    )
    intended_target_poplulation: str | None = Field(
        validation_alias="Intended target population"
    )

    combatant: str | None = Field(validation_alias="Combatant individual")
    combatant_group: str | None = Field(validation_alias="Combatant group")


class AuthorityStatus(_AuthoritySourceBase):
    @computed_field
    @property
    def status_uri(self) -> URIRef:
        return mkuri(
            aaao.ZE50_Authority_Status, self.authority_status_label, "https://r11.eu/"
        )

    authority_ascribed: str = Field(validation_alias="Authority ascribed")
    authority_status_label: str = Field(validation_alias="Authority status label")

    authority_status_type: str | None = Field(validation_alias="Status type")
    authority_ascribed_by: str | None = Field(validation_alias="Authority ascribed by")

    geographic_scope: str | None = Field(validation_alias="Geographic scope")

    temporal_start: str | None = Field(validation_alias="Temporal start")
    temporal_end: str | None = Field(validation_alias="Temporal end")


class Correspondence(_AuthoritySourceBase):
    @computed_field
    @property
    def letter_uri(self) -> URIRef:
        return mkuri(r11spec.Letter, self.letter_sent, "https://r11.eu/")

    @computed_field
    @property
    def correspondence_uri(self) -> URIRef:
        return mkuri(r11spec.Correspondence, self.letter_sent, "https://r11.eu/")

    @computed_field
    @property
    def dispatch_uri(self) -> URIRef:
        return mkuri(pwro.WE12_Sending, self.letter_sent, "https://r11.eu/")

    @computed_field
    @property
    def text_uri(self) -> URIRef:
        return mkuri(r11spec.Text_Expression, self.letter_sent, "https://r11.eu/")

    letter_sent: str = Field(validation_alias="Letter sent")
    text_therein: str = Field(validation_alias="Text therein")

    from_whom: str = Field(validation_alias="From whom")
    from_group: str | None = Field(validation_alias="From group")

    to_whom: str | None = Field(validation_alias="To whom")
    to_group: str | None = Field(validation_alias="To group")

    when_sent: str | None = Field(validation_alias="When sent")
    when_received: str | None = Field(validation_alias="When received")

    where_sent: str | None = Field(validation_alias="Where sent")
    where_received: str | None = Field(validation_alias="Where received")


class BirthAndDeath(_AuthoritySourceBase):
    who: str = Field(validation_alias="Who")
    which: TypingLiteral["Birth", "Death"] = Field(validation_alias="Which")

    when: str | None = Field(validation_alias="When")
    where: str | None = Field(validation_alias="Where")


class Boulloteria(_AuthoritySourceBase):
    @computed_field
    @property
    def boulloterion_uri(self) -> URIRef:
        return mkuri(self.boulloterion_title, "https://r11.eu/")

    boulloterion_title: str = Field(validation_alias="Boulloterion title")
    dating: str = Field(validation_alias="Dating")

    external_url: Annotated[
        AnyUrl | None, AfterValidator(lambda x: str(x) if x is not None else x)
    ] = Field(validation_alias="External URL")

    owner: str | None = Field(validation_alias="Owner")

    text_obverse: str | None = Field(validation_alias="Text obverse")
    transl_obverse: str | None = Field(validation_alias="Transl. obverse")

    text_reverse: str | None = Field(validation_alias="Text reverse")
    transl_reverse: str | None = Field(validation_alias="Transl. reverse")


class LeadSeals(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    seal_id: str = Field(validation_alias="Seal ID")
    seal_collection: str = Field(validation_alias="Seal collection")
    boulloterion: str = Field(validation_alias="Boulloterion")

    external_url: Annotated[
        AnyUrl | None, AfterValidator(lambda x: str(x) if x is not None else x)
    ] = Field(validation_alias="External url")

    @computed_field
    @property
    def seal_uri(self) -> URIRef:
        return mkuri(self.seal_id, "https://r11.eu/")

    @computed_field
    @property
    def seal_collection_uri(self) -> URIRef:
        return mkuri(self.seal_collection, "https://r11.eu/")


class OtherObjects(_AuthoritySourceBase):
    title: str = Field(validation_alias="Title")

    external_id: Annotated[
        AnyUrl | None, AfterValidator(lambda x: str(x) if x is not None else x)
    ] = Field(validation_alias="External identifier")

    description: str | None = Field(validation_alias="Description")
    object_type: str | None = Field(validation_alias="Type")

    # not in Marton sheet; default=None
    bears_text: str | None = Field(validation_alias="Bears text", default=None)

    documented_location: str | None = Field(validation_alias="Documented location")
    documented_date: str | None = Field(validation_alias="Documented date")

    creation_location: str | None = Field(validation_alias="Creation location")
    creation_date: str | None = Field(validation_alias="Creation date")

    decoration_material: str | None = Field(validation_alias="Decoration material")
    design_element: str | None = Field(validation_alias="Design element")
    material: str | None = Field(validation_alias="Material")

    # not in Marton sheet; default=None
    comissioned_by: str | None = Field(validation_alias="Comissioned by", default=None)

    owned_by_group: str | None = Field(validation_alias="Owned by group")
    owned_when: str | None = Field(validation_alias="Owned when")
    owned_where: str | None = Field(validation_alias="Owned where")


class _SingleSheetModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # mainly for person_uri

    @computed_field
    @property
    def identifier(self) -> str:
        return f"{self.name.strip()} {self.code.strip()}"

    @computed_field
    @property
    def person_uri(self) -> URIRef:
        return mkuri(self.identifier, "https://pbw2016.kdl.kcl.ac.uk/")

    @computed_field
    @property
    def publication_uri(self) -> URIRef:
        return mkuri(self.source, "https://r11.eu/")

    @computed_field
    @property
    def passage_uri(self) -> URIRef:
        return mkuri(self.publication_uri, str(self.source_loc))

    name: str = Field(validation_alias="Name")
    code: str = Field(validation_alias="Code")

    source: str = Field(validation_alias="Source")
    source_loc: Annotated[
        str, BeforeValidator(lambda x: "undefined" if x is None else x)
    ] = Field(validation_alias="Source loc")

    pbw_description: str = Field(
        validation_alias=AliasChoices("Description in PBW", "Description")
    )

    date: str | None = Field(validation_alias=AliasChoices("Death date", "Date"))
    dating_authority: str | None = Field(validation_alias="Dating authority")

    outside_source: str | None = Field(
        validation_alias="Outside Source",
        default=None,
        description="Default value required because column not in Marton sheet lol.",
    )

    notes: str | None = Field(
        validation_alias="Notes",
        default=None,
        description="Default value required because column not in Marton sheet lol.",
    )


class DeathSheetModel(_SingleSheetModel):
    pass


class LocationSheetModel(_SingleSheetModel):
    factoid_id: str | None = Field(validation_alias="Factoid ID")

    location: str | None = Field(validation_alias="Location")

    pleiades_id: str | None = Field(validation_alias="Pleiades")
    geonames_id: str | None = Field(validation_alias="Geonames")

    releven_formula: str | None = Field(
        validation_alias="Releven formula",
        default=None,
        description="Default value required because column not in Aleks sheet lol.",
    )
    releven_location_type: str | None = Field(validation_alias="RELEVEN location type")
