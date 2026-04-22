"""Base classes for triple generators."""

from collections.abc import Iterable, Iterator
from functools import cached_property
from typing import Literal as TLiteral
from typing import overload

import pandas as pd
import structlog
from lodkit import _Triple
from pydantic import BaseModel
from r11data.tabular.models import Person, _AuthoritySourceBase
from r11data.tabular.utils.df_utils import Sheets
from r11data.tabular.utils.rdf_utils import RelevenGraph, crm
from rdflib import Graph, URIRef

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

    @overload
    def lookup[_TLookupModel: BaseModel](
        self,
        sheet: pd.DataFrame,
        model: type[_TLookupModel],
        column: str,
        key: str,
        strict: TLiteral[False],
    ) -> _TLookupModel | None: ...
    @overload
    def lookup[_TLookupModel: BaseModel](
        self,
        sheet: pd.DataFrame,
        model: type[_TLookupModel],
        column: str,
        key: str,
        strict: TLiteral[True],
    ) -> _TLookupModel: ...

    def lookup[_TLookupModel: BaseModel](
        self,
        sheet: pd.DataFrame,
        model: type[_TLookupModel],
        column: str,
        key: str,
        strict: bool = True,
    ) -> _TLookupModel | None:
        """Primitive relational lookup abstraction."""
        mask = sheet[column] == key
        _row = sheet[mask]

        if _row.empty:
            msg = f"Relational lookup for '{column}' with value '{key}' failed."
            logger.warn(msg)
            if strict:
                raise RuntimeError(msg)
            return None

        row = _row.iloc[0]
        return model(**row.to_dict())

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

        Perform a lookup in the Persons sheet for the 'ID string' field
        and return a Person model instance from the first matching row.
        """
        persons_df: pd.DataFrame = self.sheets.persons
        mask = persons_df["ID string"].str.lower() == person_id.lower()
        _row = persons_df[mask]

        if _row.empty:
            msg = f"Relational lookup for Person ID '{person_id}' failed."
            logger.warn(msg)
            if strict:
                raise RuntimeError(msg)
            return None

        row = _row.iloc[0]
        return Person(**row.to_dict())

    def _p14_triples(
        self, e13_uri: URIRef, authority_uri: URIRef | None = None
    ) -> Iterator[_Triple]:
        """Perform a relational look up for an authority and assert P14 about an E13."""
        if authority_uri is None:
            authority_id = getattr(self.model, "authority", None)

            if authority_id is None:
                return

            authority_model: Person | None = self.get_person_data(
                person_id=authority_id,
                strict=False,
            )

            if authority_model is None:
                return

            authority_uri = authority_model.person_uri

        assert isinstance(authority_uri, URIRef)
        yield (e13_uri, crm.P14_carried_out_by, authority_uri)

    def _p67_triples(self, e13_uri: URIRef) -> Iterator[_Triple]:
        """Construct a passage URI and assert P67 about a passage and an E13."""

        assert isinstance(self.model, _AuthoritySourceBase)
        if (passage_uri := self.model.passage_uri) is None:
            return

        yield (passage_uri, crm.P67_refers_to, e13_uri)

    def authority_passage_triples(
        self, e13_uri: URIRef, authority_uri: URIRef | None = None
    ) -> Iterator[_Triple]:
        """Triple generator for yielding authority and passage triples."""
        yield from self._p14_triples(e13_uri=e13_uri, authority_uri=authority_uri)
        yield from self._p67_triples(e13_uri=e13_uri)


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
