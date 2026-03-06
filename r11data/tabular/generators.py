from r11data.tabular.models import (
    ActorGroup,
    AuthorGroup,
    AuthorityStatus,
    BirthAndDeath,
    Boulloteria,
    Correspondence,
    LeadSeals,
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
from r11data.tabular.utils.df_utils import Sheets
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


##################################################
#### Persons


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


persons_triples = TripleChain(
    lewis_persons_triple_generator,
    aleks_persons_triple_generator,
    marton_persons_triple_generator,
)


##################################################
#### Places

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

places_triples = TripleChain(
    lewis_places_triple_generator,
    aleks_places_triple_generator,
    marton_places_triple_generator,
)


##################################################
#### AuthorGroups

lewis_author_groups_triple_generator: TripleGenerator[AuthorGroup] = TripleGenerator(
    focus_sheet=lewis_sheets.author_groups,
    sheets=lewis_sheets,
    model_type=AuthorGroup,
    model_converter=AuthorGroupsRDFConverter,
)


aleks_author_groups_triple_generator: TripleGenerator[AuthorGroup] = TripleGenerator(
    focus_sheet=aleks_sheets.author_groups,
    sheets=aleks_sheets,
    model_type=AuthorGroup,
    model_converter=AuthorGroupsRDFConverter,
)


marton_author_groups_triple_generator: TripleGenerator[AuthorGroup] = TripleGenerator(
    focus_sheet=marton_sheets.author_groups,
    sheets=marton_sheets,
    model_type=AuthorGroup,
    model_converter=AuthorGroupsRDFConverter,
)


author_groups_triples = TripleChain(
    lewis_author_groups_triple_generator,
    aleks_author_groups_triple_generator,
    marton_author_groups_triple_generator,
)


##################################################
#### ActorGroups

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

#
actor_groups_triples = TripleChain(
    lewis_actor_groups_triple_generator,
    aleks_actor_groups_triple_generator,
    marton_actor_groups_triple_generator,
)


##################################################
#### TextPublications

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

text_publications_triples = TripleChain(
    lewis_text_publications_triple_generator,
    aleks_text_publications_triple_generator,
    marton_text_publications_triple_generator,
)

##################################################
#### Manuscripts
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

manuscripts_triples = TripleChain(
    lewis_manuscripts_triple_generator,
    aleks_manuscripts_triple_generator,
    marton_manuscripts_triple_generator,
)

##################################################
#### Birth Death

lewis_birth_death_triple_generator: TripleGenerator[BirthAndDeath] = TripleGenerator(
    focus_sheet=lewis_sheets.birth_death,
    sheets=lewis_sheets,
    model_type=BirthAndDeath,
    model_converter=BirthDeathEventRDFConverter,
)


aleks_birth_death_triple_generator: TripleGenerator[BirthAndDeath] = TripleGenerator(
    focus_sheet=aleks_sheets.birth_death,
    sheets=aleks_sheets,
    model_type=BirthAndDeath,
    model_converter=BirthDeathEventRDFConverter,
)


marton_birth_death_triple_generator: TripleGenerator[BirthAndDeath] = TripleGenerator(
    focus_sheet=marton_sheets.birth_death,
    sheets=marton_sheets,
    model_type=BirthAndDeath,
    model_converter=BirthDeathEventRDFConverter,
)

birth_death_triples = TripleChain(
    lewis_birth_death_triple_generator,
    aleks_birth_death_triple_generator,
    marton_birth_death_triple_generator,
)


##################################################
#### Social relationship

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

marton_social_relationships_triple_generator: TripleGenerator[SocialRelationship] = (
    TripleGenerator(
        focus_sheet=marton_sheets.social_relationships,
        sheets=marton_sheets,
        model_type=SocialRelationship,
        model_converter=SocialRelationshipRDFConverter,
    )
)

social_relationships_triples = TripleChain(
    lewis_social_relationships_triple_generator,
    aleks_social_relationships_triple_generator,
    marton_social_relationships_triple_generator,
)


##################################################
##################################################
#### Authority Status

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


authority_status_triples = TripleChain(
    lewis_authority_status_triple_generator,
    aleks_authority_status_triple_generator,
    marton_authority_status_triple_generator,
)

##################################################
#### Correspondence

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

correspondence_triples = TripleChain(
    lewis_correspondence_triple_generator,
    aleks_correspondence_triple_generator,
    marton_correspondence_triple_generator,
)


##################################################
#### Boulloteria

boulloteria_triples: TripleGenerator[Boulloteria] = TripleGenerator(
    focus_sheet=marton_sheets.boulloteria,
    sheets=marton_sheets,
    model_type=Boulloteria,
    model_converter=BoulloteriaRDFConverter,
)


##################################################
#### LeadSeals

lead_seals_triples: TripleGenerator[LeadSeals] = TripleGenerator(
    focus_sheet=marton_sheets.lead_seals,
    sheets=marton_sheets,
    model_type=LeadSeals,
    model_converter=LeadSealsRDFConverter,
)
