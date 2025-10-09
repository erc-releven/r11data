"""Base classes for triple generators."""

from collections.abc import Iterable, Iterator

from lodkit import _Triple
import pandas as pd
from pydantic import BaseModel
from r11data.tabular.main.utils.df_utils import Sheets
from r11data.tabular.main.utils.rdf_utils import RelevenGraph
from rdflib import Graph


class _ModelRDFConverter[_TModel: BaseModel](Iterable[_Triple]):
    def __init__(self, model: _TModel, sheets: Sheets):
        self.model = model
        self.sheets = sheets


class TripleGenerator[_TModel: BaseModel](Iterable[_Triple]):
    def __init__(
        self,
        focus_sheet: pd.DataFrame,
        sheets: Sheets,
        model_type: type[_TModel],
        model_converter: type[_ModelRDFConverter],
    ) -> None:
        self.focus_sheet = focus_sheet
        self.sheets = sheets
        self.model_type = model_type
        self.model_converter = model_converter

    def __iter__(self) -> Iterator[_Triple]:
        for _, row_series in self.focus_sheet.iterrows():
            model_instance: _TModel = self.model_type(**row_series.to_dict())
            yield from self.model_converter(model=model_instance, sheets=self.sheets)

    def to_graph(self, graph: Graph | None = None) -> Graph:
        _graph: Graph = RelevenGraph() if graph is None else graph

        for triple in self:
            _graph.add(triple)

        return _graph
