"""Triple generators for main spreadsheet RDF conversion."""

from collections.abc import Iterable, Iterator
import itertools

from lodkit import _Triple, ttl
import pandas as pd
from pydantic import BaseModel
from r11data.tabular.main.utils.rdf_utils import crm, mkuri
from rdflib import RDF, URIRef


class _ModelRDFConverter[_TModel: BaseModel](Iterable[_Triple]):
    def __init__(self, model: _TModel):
        self.model = model


class PersonRDFConverter(_ModelRDFConverter):
    def base_triples(self) -> Iterator[_Triple]:
        wisski_uri = (
            mkuri(self.model.identifier)
            if (_wisski_id := self.model.wisski_id) is None
            else URIRef(_wisski_id)
        )

        return ttl(wisski_uri, (RDF.type, crm.E21_Person))

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(self.base_triples())


class PlaceRDFConverter(_ModelRDFConverter):
    pass


class AuthorGroupRDFConverter(_ModelRDFConverter):
    pass


class TextPublicationRowRDFConverter(_ModelRDFConverter):
    pass


class TripleGenerator[_TModel: BaseModel](Iterable[_Triple]):
    def __init__(
        self,
        df: pd.DataFrame,
        model_type: type[_TModel],
        model_converter: type[_ModelRDFConverter],
    ) -> None:
        self.df = df
        self.model_type = model_type
        self.model_converter = model_converter

    def __iter__(self) -> Iterator[_Triple]:
        for _, row_series in self.df.iterrows():
            model_instance: _TModel = self.model_type(**row_series.to_dict())
            yield from self.model_converter(model=model_instance)
