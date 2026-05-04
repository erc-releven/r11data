"""The module defines TripleChain factories for Spreadsheet conversions."""

from collections.abc import Iterator

from lodkit import _Triple as Triple
from r11data.tabular.models import (
    ActorGroup,
    AuthorGroup,
    AuthorityStatus,
    BirthAndDeath,
    Boulloteria,
    Correspondence,
    DeathSheetModel,
    GeopoliticalEvent,
    Journey,
    LeadSeals,
    LocationSheetModel,
    Manuscript,
    Person,
    Place,
    SocialRelationship,
    TextPublication,
)
from r11data.tabular.triple_generators import (
    ActorGroupsRDFConverter,
    AuthorGroupsRDFConverter,
    AuthorityStatusRDFConverter,
    BirthDeathEventRDFConverter,
    CorrespondenceRDFConverter,
    DeathsTripleGenerator,
    GeopolicalEventRDFConverter,
    JourneysRDFConverter,
    LocationsTripleGenerator,
    PersonRDFConverter,
    PlaceRDFConverter,
    SocialRelationshipRDFConverter,
    TextPublicationsRDFConverter,
)
from r11data.tabular.triple_generators.bases import TripleGenerator
from r11data.tabular.triple_generators.boulloteria_triple_generator import (
    BoulloteriaRDFConverter,
)
from r11data.tabular.triple_generators.lead_seals_triple_generator import (
    LeadSealsRDFConverter,
)
from r11data.tabular.triple_generators.manuscript_triple_generator import (
    ManuscriptRDFConverter,
)
from r11data.tabular.utils.df_utils import Sheets, load_df
from r11data.tabular.utils.paths import tabular_main_sources_path
from r11data.tabular.utils.rdf_utils import (
    TripleChain,
    aleks_uri,
    lewis_uri,
    marton_uri,
)

##################################################
#### sheets

lewis_sheets_io = tabular_main_sources_path / "lewis.xlsx"
lewis_sheets: Sheets = Sheets(owner_id=lewis_uri, io=lewis_sheets_io)

aleks_sheets_io = tabular_main_sources_path / "aleks.xlsx"
aleks_sheets: Sheets = Sheets(owner_id=aleks_uri, io=aleks_sheets_io)

marton_sheets_io = tabular_main_sources_path / "marton.xlsx"
marton_sheets: Sheets = Sheets(owner_id=marton_uri, io=marton_sheets_io)


aleks_deaths_io = tabular_main_sources_path / "c11deaths-AA.xlsx"
marton_deaths_io = tabular_main_sources_path / "c11deaths-MR.xlsx"

aleks_deaths_df = load_df(aleks_deaths_io)
marton_deaths_df = load_df(marton_deaths_io)

lewis_locations_io = tabular_main_sources_path / "LFact-Lewis.xlsx"
aleks_locations_io = tabular_main_sources_path / "LFact-Aleks.xlsx"
marton_locations_io = tabular_main_sources_path / "LFact-Marton.xlsx"

lewis_locations_df = load_df(lewis_locations_io)
aleks_locations_df = load_df(aleks_locations_io)
marton_locations_df = load_df(marton_locations_io)

##################################################
#### Persons


def person_triples() -> Iterator[Triple]:
    lewis_persons_triple_generator: TripleGenerator[Person] = TripleGenerator(
        focus_sheet=lewis_sheets.persons,
        sheets=lewis_sheets,
        model_type=Person,
        model_converter=PersonRDFConverter,
    )

    aleks_persons_triple_generator: TripleGenerator[Person] = TripleGenerator(
        focus_sheet=aleks_sheets.persons,
        sheets=aleks_sheets,
        model_type=Person,
        model_converter=PersonRDFConverter,
    )

    marton_persons_triple_generator: TripleGenerator[Person] = TripleGenerator(
        focus_sheet=marton_sheets.persons,
        sheets=marton_sheets,
        model_type=Person,
        model_converter=PersonRDFConverter,
    )

    return TripleChain(
        lewis_persons_triple_generator,
        aleks_persons_triple_generator,
        marton_persons_triple_generator,
    )


##################################################
#### Places


def places_triples() -> Iterator[Triple]:
    lewis_places_triple_generator: TripleGenerator[Place] = TripleGenerator(
        focus_sheet=lewis_sheets.places,
        sheets=lewis_sheets,
        model_type=Place,
        model_converter=PlaceRDFConverter,
    )

    aleks_places_triple_generator: TripleGenerator[Place] = TripleGenerator(
        focus_sheet=aleks_sheets.places,
        sheets=aleks_sheets,
        model_type=Place,
        model_converter=PlaceRDFConverter,
    )

    marton_places_triple_generator: TripleGenerator[Place] = TripleGenerator(
        focus_sheet=marton_sheets.places,
        sheets=marton_sheets,
        model_type=Place,
        model_converter=PlaceRDFConverter,
    )

    return TripleChain(
        lewis_places_triple_generator,
        aleks_places_triple_generator,
        marton_places_triple_generator,
    )


##################################################
#### Journeys


def journeys_triples() -> Iterator[Triple]:
    lewis_journeys_triple_generator: TripleGenerator[Journey] = TripleGenerator(
        focus_sheet=lewis_sheets.journeys,
        sheets=lewis_sheets,
        model_type=Journey,
        model_converter=JourneysRDFConverter,
    )

    aleks_journeys_triple_generator: TripleGenerator[Journey] = TripleGenerator(
        focus_sheet=aleks_sheets.journeys,
        sheets=aleks_sheets,
        model_type=Journey,
        model_converter=JourneysRDFConverter,
    )

    marton_journeys_triple_generator: TripleGenerator[Journey] = TripleGenerator(
        focus_sheet=marton_sheets.journeys,
        sheets=marton_sheets,
        model_type=Journey,
        model_converter=JourneysRDFConverter,
    )

    return TripleChain(
        lewis_journeys_triple_generator,
        aleks_journeys_triple_generator,
        marton_journeys_triple_generator,
    )


##################################################
#### AuthorGroups


def author_groups_triples() -> Iterator[Triple]:
    lewis_author_groups_triple_generator: TripleGenerator[AuthorGroup] = (
        TripleGenerator(
            focus_sheet=lewis_sheets.author_groups,
            sheets=lewis_sheets,
            model_type=AuthorGroup,
            model_converter=AuthorGroupsRDFConverter,
        )
    )

    aleks_author_groups_triple_generator: TripleGenerator[AuthorGroup] = (
        TripleGenerator(
            focus_sheet=aleks_sheets.author_groups,
            sheets=aleks_sheets,
            model_type=AuthorGroup,
            model_converter=AuthorGroupsRDFConverter,
        )
    )

    marton_author_groups_triple_generator: TripleGenerator[AuthorGroup] = (
        TripleGenerator(
            focus_sheet=marton_sheets.author_groups,
            sheets=marton_sheets,
            model_type=AuthorGroup,
            model_converter=AuthorGroupsRDFConverter,
        )
    )

    return TripleChain(
        lewis_author_groups_triple_generator,
        aleks_author_groups_triple_generator,
        marton_author_groups_triple_generator,
    )


##################################################
#### ActorGroups


def actor_groups_triples() -> Iterator[Triple]:
    lewis_actor_groups_triple_generator: TripleGenerator[ActorGroup] = TripleGenerator(
        focus_sheet=lewis_sheets.actor_groups,
        sheets=lewis_sheets,
        model_type=ActorGroup,
        model_converter=ActorGroupsRDFConverter,
    )

    aleks_actor_groups_triple_generator: TripleGenerator[ActorGroup] = TripleGenerator(
        focus_sheet=aleks_sheets.actor_groups,
        sheets=aleks_sheets,
        model_type=ActorGroup,
        model_converter=ActorGroupsRDFConverter,
    )

    marton_actor_groups_triple_generator: TripleGenerator[ActorGroup] = TripleGenerator(
        focus_sheet=marton_sheets.actor_groups,
        sheets=marton_sheets,
        model_type=ActorGroup,
        model_converter=ActorGroupsRDFConverter,
    )

    return TripleChain(
        lewis_actor_groups_triple_generator,
        aleks_actor_groups_triple_generator,
        marton_actor_groups_triple_generator,
    )


##################################################
#### TextPublications


def text_publication_triples() -> Iterator[Triple]:
    lewis_text_publications_triple_generator: TripleGenerator[TextPublication] = (
        TripleGenerator(
            focus_sheet=lewis_sheets.text_publications,
            sheets=lewis_sheets,
            model_type=TextPublication,
            model_converter=TextPublicationsRDFConverter,
        )
    )

    aleks_text_publications_triple_generator: TripleGenerator[TextPublication] = (
        TripleGenerator(
            focus_sheet=aleks_sheets.text_publications,
            sheets=aleks_sheets,
            model_type=TextPublication,
            model_converter=TextPublicationsRDFConverter,
        )
    )

    marton_text_publications_triple_generator: TripleGenerator[TextPublication] = (
        TripleGenerator(
            focus_sheet=marton_sheets.text_publications,
            sheets=marton_sheets,
            model_type=TextPublication,
            model_converter=TextPublicationsRDFConverter,
        )
    )

    return TripleChain(
        lewis_text_publications_triple_generator,
        aleks_text_publications_triple_generator,
        marton_text_publications_triple_generator,
    )


##################################################
#### Manuscripts
def manuscript_triples() -> Iterator[Triple]:
    lewis_manuscripts_triple_generator: TripleGenerator[Manuscript] = TripleGenerator(
        focus_sheet=lewis_sheets.manuscripts,
        sheets=lewis_sheets,
        model_type=Manuscript,
        model_converter=ManuscriptRDFConverter,
    )

    aleks_manuscripts_triple_generator: TripleGenerator[Manuscript] = TripleGenerator(
        focus_sheet=aleks_sheets.manuscripts,
        sheets=aleks_sheets,
        model_type=Manuscript,
        model_converter=ManuscriptRDFConverter,
    )

    marton_manuscripts_triple_generator: TripleGenerator[Manuscript] = TripleGenerator(
        focus_sheet=marton_sheets.manuscripts,
        sheets=marton_sheets,
        model_type=Manuscript,
        model_converter=ManuscriptRDFConverter,
    )

    return TripleChain(
        lewis_manuscripts_triple_generator,
        aleks_manuscripts_triple_generator,
        marton_manuscripts_triple_generator,
    )


##################################################
#### Birth Death


def birth_death_triples() -> Iterator[Triple]:
    lewis_birth_death_triple_generator: TripleGenerator[BirthAndDeath] = (
        TripleGenerator(
            focus_sheet=lewis_sheets.birth_death,
            sheets=lewis_sheets,
            model_type=BirthAndDeath,
            model_converter=BirthDeathEventRDFConverter,
        )
    )

    aleks_birth_death_triple_generator: TripleGenerator[BirthAndDeath] = (
        TripleGenerator(
            focus_sheet=aleks_sheets.birth_death,
            sheets=aleks_sheets,
            model_type=BirthAndDeath,
            model_converter=BirthDeathEventRDFConverter,
        )
    )

    marton_birth_death_triple_generator: TripleGenerator[BirthAndDeath] = (
        TripleGenerator(
            focus_sheet=marton_sheets.birth_death,
            sheets=marton_sheets,
            model_type=BirthAndDeath,
            model_converter=BirthDeathEventRDFConverter,
        )
    )

    return TripleChain(
        lewis_birth_death_triple_generator,
        aleks_birth_death_triple_generator,
        marton_birth_death_triple_generator,
    )


##################################################
#### Social relationship


def social_relationships_triples() -> Iterator[Triple]:
    lewis_social_relationships_triple_generator: TripleGenerator[SocialRelationship] = (
        TripleGenerator(
            focus_sheet=lewis_sheets.social_relationships,
            sheets=lewis_sheets,
            model_type=SocialRelationship,
            model_converter=SocialRelationshipRDFConverter,
        )
    )

    aleks_social_relationships_triple_generator: TripleGenerator[SocialRelationship] = (
        TripleGenerator(
            focus_sheet=aleks_sheets.social_relationships,
            sheets=aleks_sheets,
            model_type=SocialRelationship,
            model_converter=SocialRelationshipRDFConverter,
        )
    )

    marton_social_relationships_triple_generator: TripleGenerator[
        SocialRelationship
    ] = TripleGenerator(
        focus_sheet=marton_sheets.social_relationships,
        sheets=marton_sheets,
        model_type=SocialRelationship,
        model_converter=SocialRelationshipRDFConverter,
    )

    return TripleChain(
        lewis_social_relationships_triple_generator,
        aleks_social_relationships_triple_generator,
        marton_social_relationships_triple_generator,
    )


##################################################
##################################################
#### Authority Status


def authority_status_triples() -> Iterator[Triple]:
    lewis_authority_status_triple_generator: TripleGenerator[AuthorityStatus] = (
        TripleGenerator(
            focus_sheet=lewis_sheets.authority_status,
            sheets=lewis_sheets,
            model_type=AuthorityStatus,
            model_converter=AuthorityStatusRDFConverter,
        )
    )

    aleks_authority_status_triple_generator: TripleGenerator[AuthorityStatus] = (
        TripleGenerator(
            focus_sheet=aleks_sheets.authority_status,
            sheets=aleks_sheets,
            model_type=AuthorityStatus,
            model_converter=AuthorityStatusRDFConverter,
        )
    )

    marton_authority_status_triple_generator: TripleGenerator[AuthorityStatus] = (
        TripleGenerator(
            focus_sheet=marton_sheets.authority_status,
            sheets=marton_sheets,
            model_type=AuthorityStatus,
            model_converter=AuthorityStatusRDFConverter,
        )
    )

    return TripleChain(
        lewis_authority_status_triple_generator,
        aleks_authority_status_triple_generator,
        marton_authority_status_triple_generator,
    )


##################################################
#### Correspondence


def correspondence_triples() -> Iterator[Triple]:
    lewis_correspondence_triple_generator: TripleGenerator[Correspondence] = (
        TripleGenerator(
            focus_sheet=lewis_sheets.correspondence,
            sheets=lewis_sheets,
            model_type=Correspondence,
            model_converter=CorrespondenceRDFConverter,
        )
    )

    aleks_correspondence_triple_generator: TripleGenerator[Correspondence] = (
        TripleGenerator(
            focus_sheet=aleks_sheets.correspondence,
            sheets=aleks_sheets,
            model_type=Correspondence,
            model_converter=CorrespondenceRDFConverter,
        )
    )

    marton_correspondence_triple_generator: TripleGenerator[Correspondence] = (
        TripleGenerator(
            focus_sheet=marton_sheets.correspondence,
            sheets=marton_sheets,
            model_type=Correspondence,
            model_converter=CorrespondenceRDFConverter,
        )
    )

    return TripleChain(
        lewis_correspondence_triple_generator,
        aleks_correspondence_triple_generator,
        marton_correspondence_triple_generator,
    )


##################################################
#### Boulloteria


def boulloteria_triples() -> Iterator[Triple]:
    return TripleChain(
        TripleGenerator(
            focus_sheet=marton_sheets.boulloteria,
            sheets=marton_sheets,
            model_type=Boulloteria,
            model_converter=BoulloteriaRDFConverter,
        )
    )


##################################################
#### LeadSeals


def lead_seals_triples() -> Iterator[Triple]:
    return TripleChain(
        TripleGenerator(
            focus_sheet=marton_sheets.lead_seals,
            sheets=marton_sheets,
            model_type=LeadSeals,
            model_converter=LeadSealsRDFConverter,
        )
    )


##################################################
##################################################
#### Deaths


def death_triples() -> Iterator[Triple]:
    return TripleChain(
        *[
            DeathsTripleGenerator(model=DeathSheetModel(**row.to_dict()))
            for df in [aleks_deaths_df, marton_deaths_df]
            for _, row in df.iterrows()
        ]
    )


##################################################
#### Locations


def location_triples() -> Iterator[Triple]:
    return TripleChain(
        *[
            LocationsTripleGenerator(model=LocationSheetModel(**row.to_dict()))
            for df in [lewis_locations_df, aleks_locations_df, marton_locations_df]
            for _, row in df.iterrows()
        ]
    )


##################################################
#### GeopolicialEvents


def geopolitical_event_triples() -> Iterator[Triple]:
    lewis_geo_events_triple_generator: TripleGenerator[GeopoliticalEvent] = (
        TripleGenerator(
            focus_sheet=lewis_sheets.geopolitical_events,
            sheets=lewis_sheets,
            model_type=GeopoliticalEvent,
            model_converter=GeopolicalEventRDFConverter,
        )
    )

    aleks_geo_events_triple_generator: TripleGenerator[GeopoliticalEvent] = (
        TripleGenerator(
            focus_sheet=aleks_sheets.geopolitical_events,
            sheets=aleks_sheets,
            model_type=GeopoliticalEvent,
            model_converter=GeopolicalEventRDFConverter,
        )
    )

    marton_geo_events_triple_generator: TripleGenerator[GeopoliticalEvent] = (
        TripleGenerator(
            focus_sheet=marton_sheets.geopolitical_events,
            sheets=marton_sheets,
            model_type=GeopoliticalEvent,
            model_converter=GeopolicalEventRDFConverter,
        )
    )

    return TripleChain(
        lewis_geo_events_triple_generator,
        aleks_geo_events_triple_generator,
        marton_geo_events_triple_generator,
    )
