from r11data.tabular.main.models import Person
from r11data.tabular.main.triple_generators import PersonRDFConverter
from r11data.tabular.main.triple_generators.bases import TripleGenerator
from r11data.tabular.main.utils.df_utils import Sheets
from r11data.tabular.main.utils.paths import tabular_main_sources_path
from r11data.tabular.main.utils.rdf_utils import RelevenGraph, aleks_uri, lewis_uri


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


#### Lewis
lewis_sheets_io = tabular_main_sources_path / "lewis.xlsx"
lewis_sheets: Sheets = Sheets(owner_id=lewis_uri, io=lewis_sheets_io)


lewis_person_triple_generator: TripleGenerator[Person] = TripleGenerator(
    focus_sheet=lewis_sheets.persons,
    sheets=lewis_sheets,
    model_type=Person,
    model_converter=PersonRDFConverter,
)


lewis_persons_graph: RelevenGraph = lewis_person_triple_generator.to_graph()
print(len(lewis_persons_graph))

#### Aleks
aleks_sheets_io = tabular_main_sources_path / "aleks.xlsx"
aleks_sheets: Sheets = Sheets(owner_id=aleks_uri, io=aleks_sheets_io)


aleks_person_triple_generator: TripleGenerator[Person] = TripleGenerator(
    focus_sheet=aleks_sheets.persons,
    sheets=aleks_sheets,
    model_type=Person,
    model_converter=PersonRDFConverter,
)


# aleks_persons_graph: RelevenGraph = aleks_person_triple_generator.to_graph()
# print(len(aleks_persons_graph))
