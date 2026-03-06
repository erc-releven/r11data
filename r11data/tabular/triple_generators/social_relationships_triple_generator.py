"""TripleGenerator for the Social Relationship sheet."""

from collections.abc import Iterator
from functools import cached_property
import itertools

from lodkit import _Triple, ttl
from r11data.tabular.models import SocialRelationship
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.rdf_utils import crm, mkuri, r11pros, r11spec, star, tara_uri
from rdflib import Literal, RDF, RDFS, URIRef
import structlog


logger = structlog.get_logger()


class SocialRelationshipRDFConverter(_ModelRDFConverter[SocialRelationship]):
    @cached_property
    def main_person_uri(self) -> URIRef:
        person_model = self.get_person_data(self.model.main_person, strict=True)

        person_uri: URIRef = (
            mkuri(person_model.identifier, person_model.service)
            if (_wisski_id := person_model.wisski_id) is None
            else URIRef(str(_wisski_id))
        )
        return person_uri

    @cached_property
    def related_person_uri(self) -> URIRef:
        person_model = self.get_person_data(self.model.related_person)

        person_uri: URIRef = (
            mkuri(person_model.identifier, person_model.service)
            if (_wisski_id := person_model.wisski_id) is None
            else URIRef(str(_wisski_id))
        )
        return person_uri

    def relationship_base_triples(self) -> Iterator[_Triple]:
        self.social_relationship_uri = mkuri(
            self.main_person_uri, self.related_person_uri
        )
        e13_sdhss_p16_uri, e13_sdhss_p17_uri, e13_sdhss_p18_uri, e17_uri = (
            mkuri(),
            mkuri(),
            mkuri(),
            mkuri(),
        )

        yield (self.social_relationship_uri, RDF.type, r11pros.C3)

        yield from ttl(
            e13_sdhss_p17_uri,
            (RDF.type, star.E13_sdhss_P17),
            (crm.P140_assigned_attribute_to, self.social_relationship_uri),
            (crm.P141_assigned, self.main_person_uri),
        )

        yield from ttl(
            e13_sdhss_p18_uri,
            (RDF.type, star.E13_sdhss_P18),
            (crm.P140_assigned_attribute_to, self.social_relationship_uri),
            (crm.P141_assigned, self.related_person_uri),
        )

        yield from ttl(
            e13_sdhss_p16_uri,
            (RDF.type, star.E13_sdhss_P16),
            (crm.P140_assigned_attribute_to, self.social_relationship_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri(self.model.relationship_type),
                    (RDF.type, r11pros.C4),
                    (RDFS.label, self.model.relationship_type),
                ),
            ),
        )

        yield from ttl(
            e17_uri,
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
                    mkuri("RelationshipCategory: Kinship"),
                    (RDF.type, r11spec.RelationshipCategory),
                    (RDFS.label, "Kinship"),
                ),
            ),
        )

        # p14/p17/p67 assertions
        for node in (e13_sdhss_p16_uri, e13_sdhss_p17_uri, e13_sdhss_p18_uri):
            yield from self.authority_passage_triples(node)

    def relationship_timespan_triples(self) -> Iterator[_Triple]:
        if not self.model.start_date and self.model.end_date:
            return

        e13_crm_p4_uri, time_span_uri = mkuri(), mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_p4),
            (crm.P140_assigned_attribute_to, self.social_relationship_uri),
            (crm.P141_assigned, ttl(time_span_uri, (RDF.type, crm["E52_Time-Span"]))),
        )

        if (start_date := self.model.start_date) is not None:
            yield (time_span_uri, crm.P82a_begin_of_the_begin, Literal(start_date))

        if (end_date := self.model.end_date) is not None:
            yield (time_span_uri, crm.P82b_end_of_the_end, Literal(end_date))

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.relationship_base_triples(), self.relationship_timespan_triples()
        )
