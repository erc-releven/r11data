"""TripleGenerator for the Boulloteria sheet."""

from collections.abc import Iterator
from functools import cached_property
import itertools

from lodkit import _Triple, ttl
from r11data.tabular.main.models import Boulloteria, LeadSeals, Person
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import crm, mkuri, r11spec, so, star
from rdflib import RDF, RDFS, URIRef


class BoulloteriaRDFConverter(_ModelRDFConverter[Boulloteria]):
    @cached_property
    def boulloterion_uri(self) -> URIRef:
        return mkuri(self.model.boulloterion_title)

    def base_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.boulloterion_uri,
            (RDF.type, r11spec.Boulloterion),
            (RDFS.label, self.model.boulloterion_title),
        )

        if (external_url := self.model.external_url) is not None:
            yield (URIRef(str(external_url)), so.ID7_matches, self.boulloterion_uri)

    def id_assertion_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            mkuri(),
            (RDF.type, crm.E15_Identifier_Assignment),
            (crm.P140_assigned_attribute_to, self.boulloterion_uri),
            (
                crm.P37_assigned,
                ttl(
                    mkuri(),
                    (RDF.type, crm.E42_Identifier),
                    (
                        crm.P190_has_symbolic_content,
                        f"{self.model.boulloterion_title} (Boulloterion ID)",
                    ),
                ),
            ),
        )

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
        seal_uri = mkuri(seal_model.seal_id)  # connection to seal triple generator

        yield from ttl(
            e13_spec_l1_uri,
            (RDF.type, star.E13_spec_L1),
            (crm.P140_assigned_attribute_to, self.boulloterion_uri),
            (crm.P141_assigned, seal_uri),
        )

        yield from self.authority_passage_triples(e13_spec_l1_uri)

    def ownership_triples(self) -> Iterator[_Triple]:
        e13_crm_p24_uri, e13_crm_p4_uri = mkuri(), mkuri()
        ownership_uri = mkuri()

        # ownership: base
        yield from ttl(
            e13_crm_p24_uri,
            (RDF.type, star.E13_crm_P24),
            (
                crm.P140_assigned_attribute_to,
                ttl(ownership_uri, (RDF.type, crm.E8_Acquisition)),
            ),
            (crm.P141_assigned, self.boulloterion_uri),
        )

        # ownership: timeframe
        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, ownership_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri(),
                    (RDF.type, crm["E52_Time-Span"]),
                    (RDFS.label, self.model.dating),
                ),
            ),
        )

        # authority/passage triples
        yield from self.authority_passage_triples(e13_crm_p24_uri)
        yield from self.authority_passage_triples(e13_crm_p4_uri)

        # ownership: owner
        if (owner := self.model.owner) is not None:
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
