"""TripleGenerator for the Geopolitical Event sheet."""

import itertools
from collections.abc import Iterator

from lodkit import _Triple, ttl
from r11data.tabular.models import GeopoliticalEvent
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.rdf_utils import (
    crm,
    get_source_name_lang_tag,
    lrm,
    mkuri,
    pwro,
    r11,
    r11pros,
    r11spec,
    star,
)
from rdflib import RDF, RDFS, Literal, URIRef


class GeopoliticalEventRDFConverter(_ModelRDFConverter[GeopoliticalEvent]):
    def base_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.model.event_uri,
            (RDF.type, crm.E7_Activity),
            (RDFS.label, self.model.event_label),
        )

    def attack_event_assertion_triples(self) -> Iterator[_Triple]:
        e13_crm_p9_uri = mkuri()

        yield from ttl(
            e13_crm_p9_uri,
            (RDF.type, star.E13_crm_P9),
            (crm.P140_assigned_attribute_to, self.model.event_uri),
            (
                crm.P141_assigned,
                ttl(self.model.attack_event_uri, (RDF.type, pwro.WE6_Attack)),
            ),
        )

        yield from self.authority_passage_triples(e13_crm_p9_uri)

    def event_type_assertion_triples(self) -> Iterator[_Triple]:
        e17_uri = mkuri()

        yield from ttl(
            e17_uri,
            (RDF.type, crm.E17_Type_Assignment),
            (crm.P41_classified, self.model.event_uri),
            (
                crm.P42_assigned,
                ttl(
                    self.model.event_type_uri,
                    (RDF.type, r11spec.Geopolitical_Event_Type),
                    (RDFS.label, f"{self.model.event_type} (Event Type)"),
                ),
            ),
        )

        yield from self.authority_passage_triples(e17_uri)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.attack_event_assertion_triples(),
            self.event_type_assertion_triples(),
        )
