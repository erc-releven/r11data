"""Triple generators for main spreadsheet RDF conversion."""

from collections.abc import Iterable, Iterator
import itertools

from rdflib import Literal, RDF, RDFS, URIRef

from lodkit import _Triple, ttl
import pandas as pd
from pydantic import BaseModel
from r11data.tabular.main.utils.rdf_utils import (
    crm,
    get_source_name_lang_tag,
    mkuri,
    r11,
    r11pros,
    r11spec,
    star,
)


class _ModelRDFConverter[_TModel: BaseModel](Iterable[_Triple]):
    def __init__(self, model: _TModel):
        self.model = model


class PersonRDFConverter(_ModelRDFConverter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.wisski_uri = (
            mkuri(self.model.identifier)
            if (_wisski_id := self.model.wisski_id) is None
            else URIRef(_wisski_id)
        )

    def base_triples(self) -> Iterator[_Triple]:
        return ttl(
            self.wisski_uri,
            (RDF.type, crm.E21_Person),
            (RDFS.label, self.model.descriptive_name or self.model.identifier),
        )

    def id_triples(self) -> Iterator[_Triple]:
        return ttl(
            mkuri(),
            (RDF.type, crm.E15_Identifier_Assignment),
            (crm.P14_carried_out_by, URIRef("urn:lewis")),
            (crm.P140_assigned_attribute_to, self.wisski_uri),
            (
                crm.P37_assigned,
                ttl(
                    mkuri(),
                    (RDF.type, crm.E15_Identifier_Assignment),
                    (
                        crm.P37_assigned,
                        ttl(
                            mkuri(),
                            (RDF.type, crm.E42_Identifier),
                            (crm.P190_has_symbolic_content, self.model.identifier),
                        ),
                    ),
                ),
            ),
        )

    def name_in_sources_triples(self) -> Iterator[_Triple]:
        if not (self.model.name_in_sources_orig or self.model.name_in_sources_transl):
            return

        # todo: P14, P17, P67i
        yield from ttl(
            mkuri(),
            (RDF.type, star.E13_crm_P1),
            (crm.P140_assigned_attribute_to, self.wisski_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri(f"{self.model.identifier} - E33_41"),
                    (RDF.type, crm.E33_E41_Linguistic_Appellation),
                ),
            ),
        )

        if orig := self.model.name_in_sources_orig:
            yield (
                mkuri(f"{self.model.identifier} - E33_41"),
                crm.P190_has_symbolic_content,
                Literal(orig, lang=get_source_name_lang_tag(orig)),
            )
        if transl := self.model.name_in_sources_transl:
            yield (
                mkuri(f"{self.model.identifier} - E33_41"),
                crm.P190_has_symbolic_content,
                Literal(transl, lang="en"),
            )

    def gender_triples(self) -> Iterator[_Triple]:
        if not (gender := self.model.gender_assignment):
            return

        gender_assignment_uri: URIRef = mkuri()
        yield (gender_assignment_uri, RDF.type, r11.Gender_Assignment)

        yield from ttl(
            mkuri(),
            (RDF.type, star.E13_crm_P41),
            (crm.P140_assigned_attribute_to, gender_assignment_uri),
            (crm.P141_assigned, self.wisski_uri),
        )

        # todo: P14, P17, P67i
        yield from ttl(
            mkuri(),
            (RDF.type, star.E13_crm_P42),
            (crm.P140_assigned_attribute_to, gender_assignment_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri(),
                    (RDF.type, r11pros.C11),
                    (RDFS.label, gender),
                    (crm.P190_has_symbolic_value, gender),
                ),
            ),
        )

        # todo: P14, P17, P67i
        # todo: time value?
        yield from ttl(
            mkuri(),
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, gender_assignment_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri(),
                    (RDF.type, crm["E52_Time-Span"]),
                ),
            ),
        )

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.id_triples(),
            self.name_in_sources_triples(),
            self.gender_triples(),
        )


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
