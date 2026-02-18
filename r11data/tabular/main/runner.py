from collections.abc import Iterable
from pathlib import Path

from r11data.tabular.main.models import (
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
from r11data.tabular.main.triple_generators import (
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
from r11data.tabular.main.triple_generators.bases import TripleGenerator
from r11data.tabular.main.triple_generators.boulloteria_triple_generator import (
    BoulloteriaRDFConverter,
)
from r11data.tabular.main.triple_generators.lead_seals_triple_generator import (
    LeadSealsRDFConverter,
)
from r11data.tabular.main.triple_generators.manuscript_triple_generator import (
    ManuscriptRDFConverter,
)
from r11data.tabular.main.utils.df_utils import Sheets
from r11data.tabular.main.utils.paths import tabular_main_sources_path
from r11data.tabular.main.utils.rdf_utils import (
    RelevenGraph,
    TripleChain,
    aleks_uri,
    lewis_uri,
    marton_uri,
)


##################################################
##################################################
#### sheets

lewis_sheets_io = tabular_main_sources_path / "lewis.xlsx"
lewis_sheets: Sheets = Sheets(owner_id=lewis_uri, io=lewis_sheets_io)

aleks_sheets_io = tabular_main_sources_path / "aleks.xlsx"
aleks_sheets: Sheets = Sheets(owner_id=aleks_uri, io=aleks_sheets_io)

marton_sheets_io = tabular_main_sources_path / "marton.xlsx"
marton_sheets: Sheets = Sheets(owner_id=marton_uri, io=marton_sheets_io)

##################################################
##################################################
#### Persons


lewis_person_triple_generator: TripleGenerator[Person] = TripleGenerator(
    focus_sheet=lewis_sheets.persons,
    sheets=lewis_sheets,
    model_type=Person,
    model_converter=PersonRDFConverter,
)

aleks_person_triple_generator: TripleGenerator[Person] = TripleGenerator(
    focus_sheet=aleks_sheets.persons,
    sheets=aleks_sheets,
    model_type=Person,
    model_converter=PersonRDFConverter,
)


marton_person_triple_generator: TripleGenerator[Person] = TripleGenerator(
    focus_sheet=marton_sheets.persons,
    sheets=marton_sheets,
    model_type=Person,
    model_converter=PersonRDFConverter,
)


person_triples = TripleChain(
    lewis_person_triple_generator,
    aleks_person_triple_generator,
    marton_person_triple_generator,
)

# with open("./output/persons.ttl", "w") as f:
#     f.write(person_triples.to_graph().serialize())

##################################################
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

# with open("./output/places.ttl", "w") as f:
#     f.write(places_triples.to_graph().serialize())


##################################################
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


##################################################
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

##################################################
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

##################################################
##################################################
#### Manuscripts
lewis_manuscript_triple_generator: TripleGenerator[Manuscript] = TripleGenerator(
    focus_sheet=lewis_sheets.manuscripts,
    sheets=lewis_sheets,
    model_type=Manuscript,
    model_converter=ManuscriptRDFConverter,
)

aleks_manuscript_triple_generator: TripleGenerator[Manuscript] = TripleGenerator(
    focus_sheet=aleks_sheets.manuscripts,
    sheets=aleks_sheets,
    model_type=Manuscript,
    model_converter=ManuscriptRDFConverter,
)


marton_manuscript_triple_generator: TripleGenerator[Manuscript] = TripleGenerator(
    focus_sheet=marton_sheets.manuscripts,
    sheets=marton_sheets,
    model_type=Manuscript,
    model_converter=ManuscriptRDFConverter,
)

##################################################
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


##################################################
##################################################
#### Social relationship

lewis_social_relationship_triple_generator: TripleGenerator[SocialRelationship] = (
    TripleGenerator(
        focus_sheet=lewis_sheets.social_relationships,
        sheets=lewis_sheets,
        model_type=SocialRelationship,
        model_converter=SocialRelationshipRDFConverter,
    )
)

aleks_social_relationship_triple_generator: TripleGenerator[SocialRelationship] = (
    TripleGenerator(
        focus_sheet=aleks_sheets.social_relationships,
        sheets=aleks_sheets,
        model_type=SocialRelationship,
        model_converter=SocialRelationshipRDFConverter,
    )
)

marton_social_relationship_triple_generator: TripleGenerator[SocialRelationship] = (
    TripleGenerator(
        focus_sheet=marton_sheets.social_relationships,
        sheets=marton_sheets,
        model_type=SocialRelationship,
        model_converter=SocialRelationshipRDFConverter,
    )
)

social_relationship_triples = TripleChain(
    lewis_social_relationship_triple_generator,
    aleks_social_relationship_triple_generator,
    marton_social_relationship_triple_generator,
)


# with open("./output/social_relations.ttl", "w") as f:
#     f.write(social_relationship_triples.to_graph().serialize())

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


##################################################
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

# lewis_correspondence_graph = lewis_correspondence_triple_generator.to_graph()
# lewis_correspondence_graph.serialize()
# print(len(lewis_correspondence_graph))


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


##################################################
##################################################
#### Boulloteria

marton_boulloteria_triple_generator: TripleGenerator[Boulloteria] = TripleGenerator(
    focus_sheet=marton_sheets.boulloteria,
    sheets=marton_sheets,
    model_type=Boulloteria,
    model_converter=BoulloteriaRDFConverter,
)


##################################################
##################################################
#### LeadSeals

marton_lead_seals_triple_generator: TripleGenerator[LeadSeals] = TripleGenerator(
    focus_sheet=marton_sheets.lead_seals,
    sheets=marton_sheets,
    model_type=LeadSeals,
    model_converter=LeadSealsRDFConverter,
)
