"""TripleGenerator for the Social Relationship sheet."""

import itertools
from collections.abc import Iterator
from functools import cached_property

from lodkit import _Triple, ttl
from r11data.tabular.models import SocialRelationship
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.date_parser import generate_date_triples
from r11data.tabular.utils.rdf_utils import (
    crm,
    mkuri,
    r11pros,
    r11spec,
    star,
    tara_uri,
)
from rdflib import RDF, RDFS, URIRef


class SocialRelationshipRDFConverter(_ModelRDFConverter[SocialRelationship]):
    @cached_property
    def main_person_uri(self) -> URIRef:
        person_model = self.get_person_data(self.model.main_person, strict=True)
        return person_model.person_uri

    @cached_property
    def related_person_uri(self) -> URIRef:
        person_model = self.get_person_data(self.model.related_person, strict=True)
        return person_model.person_uri

    @cached_property
    def social_relationship_uri(self) -> URIRef:
        return mkuri(r11pros.C3, self.main_person_uri, self.related_person_uri)

    def relationship_base_triples(self) -> Iterator[_Triple]:
        yield (self.social_relationship_uri, RDF.type, r11pros.C3)

        yield from ttl(
            e13_sdhss_p17_uri := mkuri(),
            (RDF.type, star.E13_sdhss_P17),
            (crm.P140_assigned_attribute_to, self.social_relationship_uri),
            (crm.P141_assigned, self.main_person_uri),
        )

        yield from ttl(
            e13_sdhss_p18_uri := mkuri(),
            (RDF.type, star.E13_sdhss_P18),
            (crm.P140_assigned_attribute_to, self.social_relationship_uri),
            (crm.P141_assigned, self.related_person_uri),
        )

        yield from ttl(
            e13_sdhss_p16_uri := mkuri(),
            (RDF.type, star.E13_sdhss_P16),
            (crm.P140_assigned_attribute_to, self.social_relationship_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri(r11pros.C4, self.model.relationship_type),
                    (RDF.type, r11pros.C4),
                    (RDFS.label, self.model.relationship_type),
                ),
            ),
        )

        yield from ttl(
            mkuri(),
            (RDF.type, crm.E17_Type_Assignment),
            (crm.P14_carried_out_by, tara_uri),
            (
                crm.P41_classified,
                ttl(
                    mkuri(self.model.relationship_type),
                    (RDF.type, crm.E55_Type),
                    (RDFS.label, self.model.relationship_type),
                ),
            ),
            (
                crm.P42_assigned,
                ttl(
                    mkuri(r11spec.Relationship_Category, "Kinship"),
                    (RDF.type, r11spec.Relationship_Category),
                    (RDFS.label, "Kinship"),
                ),
            ),
        )

        for node in (e13_sdhss_p16_uri, e13_sdhss_p17_uri, e13_sdhss_p18_uri):
            yield from self.authority_passage_triples(node)

    def relationship_timespan_triples(self) -> Iterator[_Triple]:
        if not (self.model.start_date or self.model.end_date):
            return

        e13_crm_p4_uri, e52_uri = mkuri(), mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.social_relationship_uri),
            (crm.P141_assigned, ttl(e52_uri, (RDF.type, crm["E52_Time-Span"]))),
        )

        if (start_date := self.model.start_date) is not None:
            yield from generate_date_triples(e52_uri, start_date)

        if (end_date := self.model.end_date) is not None:
            yield from generate_date_triples(e52_uri, end_date)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.relationship_base_triples(), self.relationship_timespan_triples()
        )
