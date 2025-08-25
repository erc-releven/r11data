from r11data.tabular.main.models import Person
from r11data.tabular.main.triple_generators import PersonRDFConverter, TripleGenerator
from r11data.tabular.main.utils.df_utils import SheetLoader
from r11data.tabular.main.utils.paths import tabular_main_sources_path
from r11data.tabular.main.utils.rdf_utils import RelevenGraph


lewis_sheet_loader = SheetLoader(tabular_main_sources_path / "lewis.xlsx")
lewis_persons_sheet = lewis_sheet_loader.load_persons_sheet()

# lewis_persons_triples = TripleGenerator(
#     df=lewis_persons_sheet, model_type=Person, model_converter=PersonRDFConverter
# )

# graph = RelevenGraph()

# for triple in lewis_persons_triples:
#     graph.add(triple)

# print(len(graph))

########################################
test_joe_df = lewis_persons_sheet.iloc[[254]]
test_lewis_person_triples = TripleGenerator(
    df=test_joe_df, model_type=Person, model_converter=PersonRDFConverter
)


graph = RelevenGraph()

for triple in test_lewis_person_triples:
    graph.add(triple)

# print(len(graph))
print(graph.serialize())
