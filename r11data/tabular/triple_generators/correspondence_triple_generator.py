"""TripleGenerator for the Correspondence sheet."""

import itertools
from collections.abc import Iterator

from lodkit import _Triple, ttl
from r11data.tabular.models import Correspondence, Place
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.date_parser import generate_date_triples
from r11data.tabular.utils.rdf_utils import crm, mkuri, pwro, r11spec, star
from rdflib import RDF, RDFS


class CorrespondenceRDFConverter(_ModelRDFConverter[Correspondence]):
    def base_triples(self) -> Iterator[_Triple]:
        return ttl(
            self.model.correspondence_uri,
            (RDF.type, r11spec.Correspondence),
            (RDFS.label, f"{self.model.letter_sent} (Correspondence)"),
        )

    def letter_triples(self) -> Iterator[_Triple]:
        e13_crm_p128_uri, e13_spec_l2_uri, e13_crm_p106 = (
            mkuri(),
            mkuri(),
            mkuri(),
        )

        yield from ttl(
            e13_crm_p128_uri,
            (RDF.type, star.E13_crm_P128),
            (crm.P140_assigned_attribute_to, self.model.correspondence_uri),
            (
                crm.P141_assigned,
                ttl(
                    self.model.letter_uri,
                    (RDF.type, r11spec.Letter),
                    (RDFS.label, f"{self.model.letter_sent} (Letter)"),
                ),
            ),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p128_uri)

        yield from ttl(
            e13_crm_p106,
            (RDF.type, star.E13_crm_P106),
            (crm.P140_assigned_attribute_to, self.model.letter_uri),
            (
                crm.P141_assigned,
                ttl(
                    self.model.text_uri,
                    (RDF.type, r11spec.Text_Expression),
                    (RDFS.label, self.model.text_therein),
                ),
            ),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p106)

        # 'from whom' information is currently implicit in the model
        # to whom (optional)
        if (to_whom := self.model.to_whom) is not None:
            person_model = self.get_person_data(to_whom)

            yield from ttl(
                e13_spec_l2_uri,
                (RDF.type, star.E13_spec_L2),
                (crm.P140_assigned_attribute_to, self.model.letter_uri),
                (crm.P141_assigned, person_model.person_uri),
            )

            # authority + passage triples
            yield from self.authority_passage_triples(e13_spec_l2_uri)

    def dispatch_triples(self) -> Iterator[_Triple]:
        e13_crm_p25_uri = mkuri()

        yield from ttl(
            e13_crm_p25_uri,
            (RDF.type, star.E13_crm_P25),
            (
                crm.P140_assigned_attribute_to,
                ttl(self.model.dispatch_uri, (RDF.type, pwro.WE12_Sending)),
            ),
            (crm.P141_assigned, self.model.correspondence_uri),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p25_uri)

        # dispatch from
        if (where_sent := self.model.where_sent) is not None:
            e13_pwro_wp13_uri = mkuri()

            where_sent_model: Place = self.lookup(
                sheet=self.sheets.places,
                model=Place,
                column="Reference name",
                key=where_sent,
                strict=True,
            )

            yield from ttl(
                e13_pwro_wp13_uri,
                (RDF.type, star.E13_pwro_WP13),
                (crm.P140_assigned_attribute_to, self.model.dispatch_uri),
                (
                    crm.P141_assigned,
                    ttl(
                        where_sent_model.place_uri,
                        (RDF.type, crm.E27_Site),
                        (RDFS.label, where_sent),
                    ),
                ),
            )

            # authority + passage triples
            yield from self.authority_passage_triples(e13_pwro_wp13_uri)

        # dispatch from to
        if (where_received := self.model.where_received) is not None:
            e13_pwro_wp4_uri = mkuri()

            where_received_model: Place = self.lookup(
                sheet=self.sheets.places,
                model=Place,
                column="Reference name",
                key=where_received,
                strict=True,
            )

            yield from ttl(
                e13_pwro_wp4_uri,
                (RDF.type, star.E13_pwro_WP9),
                (crm.P140_assigned_attribute_to, self.model.dispatch_uri),
                (
                    crm.P141_assigned,
                    ttl(
                        where_received_model.place_uri,
                        (RDF.type, crm.E27_Site),
                        (RDFS.label, where_received),
                    ),
                ),
            )

            # authority + passage triples
            yield from self.authority_passage_triples(e13_pwro_wp4_uri)

    def dispatch_date_assertion_triples(self) -> Iterator[_Triple]:
        """Note: `When received` is currently not defined in the model."""
        if (when_sent := self.model.when_sent) is None:
            return

        e13_crm_p4_uri = mkuri()
        e52_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.model.dispatch_uri),
            (crm.P141_assigned, ttl(e52_uri, (RDF.type, crm["E52_Time-Span"]))),
        )

        yield from generate_date_triples(e52_uri, when_sent)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.letter_triples(),
            self.dispatch_triples(),
            self.dispatch_date_assertion_triples(),
        )
