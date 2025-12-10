from collections.abc import Iterator

from lodkit import _Triple
from r11data.tabular.main.models import (
    ActorGroup,
    AuthorGroup,
    BirthAndDeath,
    Manuscript,
    Person,
    Place,
    SocialRelationship,
    TextPublication,
)
from r11data.tabular.main.triple_generators import (
    ActorGroupsRDFConverter,
    AuthorGroupsRDFConverter,
    BirthDeathEventRDFConverter,
    PersonRDFConverter,
    PlaceRDFConverter,
    SocialRelationshipRDFConverter,
    TextPublicationsRDFConverter,
)
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.triple_generators.bases import TripleGenerator
from r11data.tabular.main.triple_generators.manuscript_triple_generator import (
    ManuscriptRDFConverter,
)
from r11data.tabular.main.utils.df_utils import Sheets
from r11data.tabular.main.utils.paths import tabular_main_sources_path
from r11data.tabular.main.utils.rdf_utils import (
    RelevenGraph,
    aleks_uri,
    lewis_uri,
    marton_uri,
)
from rdflib import Literal, URIRef


##################################################
# #### spot-check generated triples

# # test_ioannes_df: pd.DataFrame = lewis_persons_sheet.iloc[[254]]

# # test_lewis_person_triples = TripleGenerator(
# #     df=test_ioannes_df,
# #     sheets=lewis_sheet_loader,
# #     model_type=Person,
# #     model_converter=PersonRDFConverter,
# # )


# # graph = RelevenGraph()

# # for triple in test_lewis_person_triples:
# #     graph.add(triple)

# # print(len(graph))
# # print(graph.serialize())

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


# lewis_persons_graph: RelevenGraph = lewis_person_triple_generator.to_graph()
# lewis_persons_graph.serialize()
# print(len(lewis_persons_graph))


aleks_person_triple_generator: TripleGenerator[Person] = TripleGenerator(
    focus_sheet=aleks_sheets.persons,
    sheets=aleks_sheets,
    model_type=Person,
    model_converter=PersonRDFConverter,
)


# aleks_persons_graph: RelevenGraph = aleks_person_triple_generator.to_graph()
# aleks_persons_graph.serialize()
# print(len(aleks_persons_graph))


marton_person_triple_generator: TripleGenerator[Person] = TripleGenerator(
    focus_sheet=marton_sheets.persons,
    sheets=marton_sheets,
    model_type=Person,
    model_converter=PersonRDFConverter,
)


# marton_persons_graph: RelevenGraph = marton_person_triple_generator.to_graph()
# marton_persons_graph.serialize()
# print(len(marton_persons_graph))

##################################################
##################################################
#### Places

lewis_places_triple_generator: TripleGenerator[Place] = TripleGenerator(
    focus_sheet=lewis_sheets.places,
    sheets=lewis_sheets,
    model_type=Place,
    model_converter=PlaceRDFConverter,
)

# lewis_places_graph: RelevenGraph = lewis_places_triple_generator.to_graph()
# lewis_places_graph.serialize()
# print(len(lewis_places_graph))


aleks_places_triple_generator: TripleGenerator[Place] = TripleGenerator(
    focus_sheet=aleks_sheets.places,
    sheets=aleks_sheets,
    model_type=Place,
    model_converter=PlaceRDFConverter,
)

# aleks_places_graph: RelevenGraph = aleks_places_triple_generator.to_graph()
# aleks_places_graph.serialize()
# print(len(aleks_places_graph))


marton_places_triple_generator: TripleGenerator[Place] = TripleGenerator(
    focus_sheet=marton_sheets.places,
    sheets=marton_sheets,
    model_type=Place,
    model_converter=PlaceRDFConverter,
)

# marton_places_graph: RelevenGraph = marton_places_triple_generator.to_graph()
# marton_places_graph.serialize()
# print(len(marton_places_graph))

##################################################
##################################################
#### AuthorGroups

lewis_author_groups_triple_generator: TripleGenerator[AuthorGroup] = TripleGenerator(
    focus_sheet=lewis_sheets.author_groups,
    sheets=lewis_sheets,
    model_type=AuthorGroup,
    model_converter=AuthorGroupsRDFConverter,
)


# lewis_author_groups_graph = lewis_author_groups_triple_generator.to_graph()
# lewis_author_groups_graph.serialize()
# print(len(lewis_author_groups_graph))


aleks_author_groups_triple_generator: TripleGenerator[AuthorGroup] = TripleGenerator(
    focus_sheet=aleks_sheets.author_groups,
    sheets=aleks_sheets,
    model_type=AuthorGroup,
    model_converter=AuthorGroupsRDFConverter,
)

# aleks_author_groups_graph = aleks_author_groups_triple_generator.to_graph()
# aleks_author_groups_graph.serialize()
# print(len(aleks_author_groups_graph))


marton_author_groups_triple_generator: TripleGenerator[AuthorGroup] = TripleGenerator(
    focus_sheet=marton_sheets.author_groups,
    sheets=marton_sheets,
    model_type=AuthorGroup,
    model_converter=AuthorGroupsRDFConverter,
)

# marton_author_groups_graph = marton_author_groups_triple_generator.to_graph()
# marton_author_groups_graph.serialize()
# print(len(marton_author_groups_graph))


##################################################
##################################################
#### ActorGroups


lewis_actor_groups_triple_generator: TripleGenerator[ActorGroup] = TripleGenerator(
    focus_sheet=lewis_sheets.actor_groups,
    sheets=lewis_sheets,
    model_type=ActorGroup,
    model_converter=ActorGroupsRDFConverter,
)


# lewis_actor_groups_graph = lewis_actor_groups_triple_generator.to_graph()
# lewis_actor_groups_graph.serialize()
# print(len(lewis_actor_groups_graph))


aleks_actor_groups_triple_generator: TripleGenerator[ActorGroup] = TripleGenerator(
    focus_sheet=aleks_sheets.actor_groups,
    sheets=aleks_sheets,
    model_type=ActorGroup,
    model_converter=ActorGroupsRDFConverter,
)

# aleks_author_groups_graph = aleks_author_groups_triple_generator.to_graph()
# aleks_author_groups_graph.serialize()
# print(len(aleks_author_groups_graph))


marton_actor_groups_triple_generator: TripleGenerator[ActorGroup] = TripleGenerator(
    focus_sheet=marton_sheets.actor_groups,
    sheets=marton_sheets,
    model_type=ActorGroup,
    model_converter=ActorGroupsRDFConverter,
)

# marton_actor_groups_graph = marton_actor_groups_triple_generator.to_graph()
# marton_actor_groups_graph.serialize()
# print(len(marton_actor_groups_graph))

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


# lewis_text_publications_graph = lewis_text_publications_triple_generator.to_graph()
# lewis_text_publications_graph.serialize()
# print(len(lewis_text_publications_graph))


aleks_text_publications_triple_generator: TripleGenerator[TextPublication] = (
    TripleGenerator(
        focus_sheet=aleks_sheets.text_publications,
        sheets=aleks_sheets,
        model_type=TextPublication,
        model_converter=TextPublicationsRDFConverter,
    )
)

# aleks_text_publications_graph = aleks_text_publications_triple_generator.to_graph()
# aleks_text_publications_graph.serialize()
# print(len(aleks_text_publications_graph))


marton_text_publications_triple_generator: TripleGenerator[TextPublication] = (
    TripleGenerator(
        focus_sheet=marton_sheets.text_publications,
        sheets=marton_sheets,
        model_type=TextPublication,
        model_converter=TextPublicationsRDFConverter,
    )
)

# marton_text_publications_graph = marton_text_publications_triple_generator.to_graph()
# marton_text_publications_graph.serialize()
# print(len(marton_text_publications_graph))

##################################################
##################################################
#### Manuscripts
lewis_manuscript_triple_generator: TripleGenerator[Manuscript] = TripleGenerator(
    focus_sheet=lewis_sheets.manuscripts,
    sheets=lewis_sheets,
    model_type=Manuscript,
    model_converter=ManuscriptRDFConverter,
)

# lewis_manuscript_graph = lewis_manuscript_triple_generator.to_graph()
# lewis_manuscript_graph.serialize()
# print(len(lewis_manuscript_graph))

aleks_manuscript_triple_generator: TripleGenerator[Manuscript] = TripleGenerator(
    focus_sheet=aleks_sheets.manuscripts,
    sheets=aleks_sheets,
    model_type=Manuscript,
    model_converter=ManuscriptRDFConverter,
)

# aleks_manuscript_graph = aleks_manuscript_triple_generator.to_graph()
# aleks_manuscript_graph.serialize()
# print(len(aleks_manuscript_graph))

marton_manuscript_triple_generator: TripleGenerator[Manuscript] = TripleGenerator(
    focus_sheet=marton_sheets.manuscripts,
    sheets=marton_sheets,
    model_type=Manuscript,
    model_converter=ManuscriptRDFConverter,
)

# marton_manuscript_graph = marton_manuscript_triple_generator.to_graph()
# marton_manuscript_graph.serialize()
# print(len(marton_manuscript_graph))

##################################################
##################################################
#### Birth Death

# lewis_birth_death_triple_generator: TripleGenerator[BirthAndDeath] = TripleGenerator(
#     focus_sheet=lewis_sheets.birth_death,
#     sheets=lewis_sheets,
#     model_type=BirthAndDeath,
#     model_converter=BirthDeathEventRDFConverter,
# )

# lewis_birth_death_graph = lewis_birth_death_triple_generator.to_graph()
# lewis_birth_death_graph.serialize()
# print(len(lewis_birth_death_graph))

# aleks_birth_death_triple_generator: TripleGenerator[BirthAndDeath] = TripleGenerator(
#     focus_sheet=aleks_sheets.birth_death,
#     sheets=aleks_sheets,
#     model_type=BirthAndDeath,
#     model_converter=BirthDeathEventRDFConverter,
# )

# aleks_birth_death_graph = aleks_birth_death_triple_generator.to_graph()
# aleks_birth_death_graph.serialize()
# print(len(aleks_birth_death_graph))


# marton_birth_death_triple_generator: TripleGenerator[BirthAndDeath] = TripleGenerator(
#     focus_sheet=marton_sheets.birth_death,
#     sheets=marton_sheets,
#     model_type=BirthAndDeath,
#     model_converter=BirthDeathEventRDFConverter,
# )

# marton_birth_death_graph = marton_birth_death_triple_generator.to_graph()
# marton_birth_death_graph.serialize()
# print(len(marton_birth_death_graph))

##################################################
##################################################


lewis_social_relationship_triple_generator: TripleGenerator[SocialRelationship] = (
    TripleGenerator(
        focus_sheet=lewis_sheets.social_relationships,
        sheets=lewis_sheets,
        model_type=SocialRelationship,
        model_converter=SocialRelationshipRDFConverter,
    )
)

# lewis_social_relationship_graph = lewis_social_relationship_triple_generator.to_graph()
# lewis_social_relationship_graph.serialize()
# print(len(lewis_social_relationship_graph))

aleks_social_relationship_triple_generator: TripleGenerator[SocialRelationship] = (
    TripleGenerator(
        focus_sheet=aleks_sheets.social_relationships,
        sheets=aleks_sheets,
        model_type=SocialRelationship,
        model_converter=SocialRelationshipRDFConverter,
    )
)

# aleks_social_relationship_graph = aleks_social_relationship_triple_generator.to_graph()
# aleks_social_relationship_graph.serialize()
# print(len(aleks_social_relationship_graph))

marton_social_relationship_triple_generator: TripleGenerator[SocialRelationship] = (
    TripleGenerator(
        focus_sheet=marton_sheets.social_relationships,
        sheets=marton_sheets,
        model_type=SocialRelationship,
        model_converter=SocialRelationshipRDFConverter,
    )
)

# marton_social_relationship_graph = (
#     marton_social_relationship_triple_generator.to_graph()
# )
# marton_social_relationship_graph.serialize()
# print(len(marton_social_relationship_graph))
