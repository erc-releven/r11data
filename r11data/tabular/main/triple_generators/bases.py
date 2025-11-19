"""Base classes for triple generators."""

from collections.abc import Iterable, Iterator
from functools import cached_property
from typing import Literal as TLiteral, overload

from lodkit import _Triple
import pandas as pd
from pydantic import BaseModel
from r11data.tabular.main.models import Person
from r11data.tabular.main.utils.df_utils import Sheets
from r11data.tabular.main.utils.rdf_utils import RelevenGraph, crm, mkuri
from rdflib import Graph, URIRef
import structlog


logger = structlog.get_logger()


class _ModelRDFConverter[_TModel: BaseModel](Iterable[_Triple]):
    def __init__(self, model: _TModel, sheets: Sheets):
        self.model = model
        self.sheets = sheets

    # this too could be generalized; but is it worth the abstraction?
    @cached_property
    def publication_label(self) -> str:
        publication = self.model.source_text_publication  # type: ignore

        publications_df: pd.DataFrame = self.sheets.text_publications
        mask = publications_df["Text identifier"] == publication
        publication_label = publications_df.loc[mask, "Edition"].iloc[0]

        return publication_label

    @overload
    def get_person_data(
        self, person_id: str, strict: TLiteral[True] = True
    ) -> Person: ...
    @overload
    def get_person_data(
        self, person_id: str, strict: TLiteral[False]
    ) -> Person | None: ...
    def get_person_data(self, person_id: str, strict: bool = True) -> Person | None:
        """Relational Persons lookup.

        Performa a lookup in the Persons sheet for the 'ID string' field
        and return a Person model instance from the first matching row.
        """
        persons_df: pd.DataFrame = self.sheets.persons
        mask = persons_df["ID string"] == person_id
        _row = persons_df[mask]

        if _row.empty:
            msg = f"Relational lookup for Person ID '{person_id}' failed."
            logger.warn(msg)
            if strict:
                raise RuntimeError(msg)
            return None

        row = _row.iloc[0]
        return Person(**row.to_dict())

    def _p14_triples(self, e13: URIRef) -> Iterator[_Triple]:
        """Perform a relational look up for an authority and assert P14 about an E13."""
        if (authority := self.model.authority) is None:
            return
        if (authority_data := self.get_person_data(authority, strict=False)) is None:
            return

        yield (e13, crm.P14_carried_out_by, authority_data.person_uri)

    def _p67_triples(self, e13: URIRef) -> Iterator[_Triple]:
        """Construct a passage URI and assert P67 about a passage and an E13."""
        reference = self.model.source_text_reference
        excerpt = self.model.source_text_excerpt

        if reference is None and excerpt is None:
            return

        passage_uri = mkuri(f"{reference} - {excerpt}")
        yield (passage_uri, crm.P67_refers_to, e13)

    def authority_passage_triples(self, e13: URIRef) -> Iterator[_Triple]:
        """Triple generator for yielding authority and passage triples."""
        yield from self._p14_triples(e13)
        yield from self._p67_triples(e13)


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


class Foo:
    def get_person_data(self, person_id: str, strict: bool = True) -> Person | None:
        pass

    def get_person_uri(self, person_id: str, strict: bool = True) -> URIRef | None:
        pass
