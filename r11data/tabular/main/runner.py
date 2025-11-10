from r11data.tabular.main.models import AuthorGroup, Person, Place
from r11data.tabular.main.triple_generators import PersonRDFConverter, PlaceRDFConverter
from r11data.tabular.main.triple_generators.author_groups_triple_generator import (
    AuthorGroupsRDFConverter,
)
from r11data.tabular.main.triple_generators.bases import TripleGenerator
from r11data.tabular.main.utils.df_utils import Sheets
from r11data.tabular.main.utils.paths import tabular_main_sources_path
from r11data.tabular.main.utils.rdf_utils import aleks_uri, lewis_uri, marton_uri


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
#### Lewis


lewis_person_triple_generator: TripleGenerator[Person] = TripleGenerator(
    focus_sheet=lewis_sheets.persons,
    sheets=lewis_sheets,
    model_type=Person,
    model_converter=PersonRDFConverter,
)


# lewis_persons_graph: RelevenGraph = lewis_person_triple_generator.to_graph()
# print(len(lewis_persons_graph))


##################################################
lewis_places_triple_generator: TripleGenerator[Place] = TripleGenerator(
    focus_sheet=lewis_sheets.places,
    sheets=lewis_sheets,
    model_type=Place,
    model_converter=PlaceRDFConverter,
)


# lewis_places_graph = lewis_places_triple_generator.to_graph()
# print(len(lewis_places_graph))
# print(lewis_places_graph.serialize())

##################################################
##################################################
#### Aleks


aleks_person_triple_generator: TripleGenerator[Person] = TripleGenerator(
    focus_sheet=aleks_sheets.persons,
    sheets=aleks_sheets,
    model_type=Person,
    model_converter=PersonRDFConverter,
)


# aleks_persons_graph: RelevenGraph = aleks_person_triple_generator.to_graph()
# print(len(aleks_persons_graph))

##################################################

aleks_places_triple_generator: TripleGenerator[Place] = TripleGenerator(
    focus_sheet=aleks_sheets.places,
    sheets=aleks_sheets,
    model_type=Place,
    model_converter=PlaceRDFConverter,
)


# aleks_places_graph: RelevenGraph = aleks_places_triple_generator.to_graph()
# print(len(aleks_places_graph))
# print(aleks_places_graph.serialize())

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
# print(len(lewis_author_groups_graph))
# print(lewis_author_groups_graph.serialize())

##################################################


aleks_author_groups_triple_generator: TripleGenerator[AuthorGroup] = TripleGenerator(
    focus_sheet=aleks_sheets.author_groups,
    sheets=aleks_sheets,
    model_type=AuthorGroup,
    model_converter=AuthorGroupsRDFConverter,
)

# aleks_author_groups_graph = aleks_author_groups_triple_generator.to_graph()
# print(len(aleks_author_groups_graph))
# print(aleks_author_groups_graph.serialize())

##################################################


marton_author_groups_triple_generator: TripleGenerator[AuthorGroup] = TripleGenerator(
    focus_sheet=marton_sheets.author_groups,
    sheets=marton_sheets,
    model_type=AuthorGroup,
    model_converter=AuthorGroupsRDFConverter,
)

# marton_author_groups_graph = marton_author_groups_triple_generator.to_graph()
# print(len(marton_author_groups_graph))
# print(marton_author_groups_graph.serialize())
