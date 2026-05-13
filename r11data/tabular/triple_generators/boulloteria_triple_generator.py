"""TripleGenerator for the Boulloteria sheet."""

import itertools
from collections.abc import Iterator

from lodkit import _Triple, ttl
from r11data.tabular.models import Boulloteria, LeadSeals, Person
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.date_parser import generate_date_triples
from r11data.tabular.utils.rdf_utils import crm, mkuri, r11spec, so, star
from rdflib import RDF, RDFS, URIRef


class BoulloteriaRDFConverter(_ModelRDFConverter[Boulloteria]):
    def base_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.model.boulloterion_uri,
            (RDF.type, r11spec.Boulloterion),
            (RDFS.label, self.model.boulloterion_title),
        )

        if (external_url := self.model.external_url) is not None:
            yield (
                URIRef(str(external_url)),
                so.ID7_matches,
                self.model.boulloterion_uri,
            )

    def id_assertion_triples(self) -> Iterator[_Triple]:
        e15_uri = mkuri()

        yield from ttl(
            e15_uri,
            (RDF.type, crm.E15_Identifier_Assignment),
            (crm.P140_assigned_attribute_to, self.model.boulloterion_uri),
            (
                crm.P37_assigned,
                ttl(
                    self.model.identifier_uri,
                    (RDF.type, crm.E42_Identifier),
                    (
                        crm.P190_has_symbolic_content,
                        f"{self.model.boulloterion_title} (Boulloterion ID)",
                    ),
                ),
            ),
        )

        yield from self.authority_passage_triples(e15_uri)

    def production_assertion_triples(self) -> Iterator[_Triple]:
        e13_crm_p108_uri = mkuri()

        yield from ttl(
            e13_crm_p108_uri,
            (RDF.type, star.E13_crm_P108),
            (crm.P140_assigned_attribute_to, self.model.boulloterion_uri),
            (crm.P141_assigned, self.model.boulloterion_production_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p108_uri)

    def production_time_span_assertion_triples(self) -> Iterator[_Triple]:
        e13_crm_p4_uri = mkuri()
        e52_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.model.boulloterion_production_uri),
            (crm.P141_assigned, ttl(e52_uri, (RDF.type, crm["E52_Time-Span"]))),
        )

        yield from generate_date_triples(e52_uri, self.model.dating)
        yield from self.authority_passage_triples(e13_crm_p4_uri)

    def produced_seal_triples(self) -> Iterator[_Triple]:
        seal_model: LeadSeals | None = self.lookup(
            self.sheets.lead_seals,
            LeadSeals,
            "Boulloterion",
            self.model.boulloterion_title,
            strict=False,
        )

        if seal_model is None:
            return

        e13_spec_l1_uri = mkuri()

        yield from ttl(
            e13_spec_l1_uri,
            (RDF.type, star.E13_spec_L1),
            (crm.P140_assigned_attribute_to, self.model.boulloterion_uri),
            (crm.P141_assigned, seal_model.seal_uri),
        )

        yield from self.authority_passage_triples(e13_spec_l1_uri)

    def ownership_triples(self) -> Iterator[_Triple]:
        e13_crm_p24_uri, e13_crm_p4_uri = mkuri(), mkuri()
        ownership_uri = mkuri()
        e52_uri = mkuri()

        # ownership: base
        yield from ttl(
            e13_crm_p24_uri,
            (RDF.type, star.E13_crm_P24),
            (
                crm.P140_assigned_attribute_to,
                ttl(ownership_uri, (RDF.type, crm.E8_Acquisition)),
            ),
            (crm.P141_assigned, self.model.boulloterion_uri),
        )

        # ownership: timeframe
        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, ownership_uri),
            (
                crm.P141_assigned,
                ttl(
                    e52_uri,
                    (RDF.type, crm["E52_Time-Span"]),
                ),
            ),
        )

        yield from generate_date_triples(e52_uri, self.model.dating)

        # authority/passage triples
        yield from self.authority_passage_triples(e13_crm_p24_uri)
        yield from self.authority_passage_triples(e13_crm_p4_uri)

        # ownership: owner
        if (owner := self.model.owner) is None:
            return

        owner_model: Person = self.get_person_data(person_id=owner)
        e13_crm_p22 = mkuri()

        yield from ttl(
            e13_crm_p22,
            (RDF.type, star.E13_crm_P22),
            (crm.P140_assigned_attribute_to, ownership_uri),
            (crm.P141_assigned, owner_model.person_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p22)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.id_assertion_triples(),
            self.produced_seal_triples(),
            self.ownership_triples(),
        )
