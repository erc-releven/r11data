"""Base classes for triple generators."""

from collections.abc import Iterable, Iterator
from functools import cached_property
from typing import overload

from pydantic import BaseModel

from lodkit import _Triple
import pandas as pd
from r11data.tabular.main.utils.df_utils import Sheets
from r11data.tabular.main.utils.rdf_utils import RelevenGraph, mkuri
from rdflib import Graph, URIRef
import structlog


logger = structlog.get_logger()


class _ModelRDFConverter[_TModel: BaseModel](Iterable[_Triple]):
    def __init__(self, model: _TModel, sheets: Sheets):
        self.model = model
        self.sheets = sheets

    @cached_property
    def publication_label(self) -> str:
        publication = self.model.source_text_publication  # type: ignore

        publications_df: pd.DataFrame = self.sheets.text_publications
        mask = publications_df["Text identifier"] == publication
        publication_label = publications_df.loc[mask, "Edition"].iloc[0]

        return publication_label

    @cached_property
    def authority_data(self) -> tuple[URIRef, str] | None:
        """Relational lookup for Authority."""

        if (authority := self.model.authority) is None:  # type: ignore
            return None

        persons_df: pd.DataFrame = self.sheets.persons
        mask = persons_df["ID string"] == authority
        _row = persons_df[mask]

        if _row.empty:
            msg = f"Relational lookup for Authority '{authority}' failed."
            logger.warn(msg)
            raise RuntimeError(msg)

        row = _row.iloc[0]

        _wisski_id = (
            URIRef(_id)
            if (_id := row["WissKI ID"]) is not None
            else mkuri(row["Identifier"])
        )
        _identifier = persons_df.loc[mask, "Identifier"].iloc[0]

        authority_uri: URIRef = (
            mkuri(_identifier) if pd.isna(_wisski_id) else URIRef(_wisski_id)
        )
        authority_label = persons_df.loc[mask, "Descriptive name"].iloc[0]

        assert authority_uri and authority_label
        return authority_uri, authority_label


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

    @overload
    def to_graph(self, graph: None = None) -> RelevenGraph: ...

    @overload
    def to_graph[TGraph: Graph](self, graph: TGraph) -> TGraph: ...

    def to_graph(self, graph: Graph | None = None) -> Graph:
        _graph: Graph = RelevenGraph() if graph is None else graph

        for triple in self:
            _graph.add(triple)

        return _graph
