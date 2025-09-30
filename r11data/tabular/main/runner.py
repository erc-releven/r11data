import pandas as pd
from r11data.tabular.main.models import Person
from r11data.tabular.main.triple_generators import PersonRDFConverter, TripleGenerator
from r11data.tabular.main.utils.df_utils import Sheets
from r11data.tabular.main.utils.paths import tabular_main_sources_path
from r11data.tabular.main.utils.rdf_utils import RelevenGraph
from r11data.utils.paths import output_tabular

########################################
#### spot-check generated triples

# test_ioannes_df: pd.DataFrame = lewis_persons_sheet.iloc[[254]]

# test_lewis_person_triples = TripleGenerator(
#     df=test_ioannes_df,
#     sheets=lewis_sheet_loader,
#     model_type=Person,
#     model_converter=PersonRDFConverter,
# )


# graph = RelevenGraph()

# for triple in test_lewis_person_triples:
#     graph.add(triple)

# print(len(graph))
# print(graph.serialize())

##################################################
aleks_sheet_loader = Sheets(tabular_main_sources_path / "aleks.xlsx")
aleks_persons_sheet: pd.DataFrame = aleks_sheet_loader.persons

aleks_graph = RelevenGraph()

person_triples = TripleGenerator(
    df=aleks_persons_sheet,
    sheets=aleks_sheet_loader,
    model_type=Person,
    model_converter=PersonRDFConverter,
)

for triple in person_triples:
    aleks_graph.add(triple)


with open(output_tabular / "aleks_persons.ttl", "w") as f:
    f.write(aleks_graph.serialize())

##################################################

lewis_sheet_loader = Sheets(tabular_main_sources_path / "lewis.xlsx")
lewis_persons_sheet: pd.DataFrame = lewis_sheet_loader.persons

lewis_graph = RelevenGraph()

lewis_persons_triples = TripleGenerator(
    df=lewis_persons_sheet,
    sheets=lewis_sheet_loader,
    model_type=Person,
    model_converter=PersonRDFConverter,
)

for triple in lewis_persons_triples:
    lewis_graph.add(triple)


with open(output_tabular / "lewis_persons.ttl", "w") as f:
    f.write(lewis_graph.serialize())
