"""TripleGenerator for the Correspondence sheet."""

from collections.abc import Iterator
import itertools

from lodkit import _Triple, ttl
from r11data.tabular.main.models import Correspondence
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import crm, mkuri, pwro, r11spec, star
from rdflib import RDF, RDFS, URIRef


class CorrespondenceRDFConverter(_ModelRDFConverter[Correspondence]):
    def base_triples(self) -> Iterator[_Triple]:
        self.correspondence_uri = mkuri(self.model.letter_sent)

        return ttl(
            self.correspondence_uri,
            (RDF.type, r11spec.Corresponence),
            (RDFS.label, f"{self.model.letter_sent} (Corresponence)"),
        )

    def letter_triples(self) -> Iterator[_Triple]:
        e13_crm_p128_uri, e13_spec_l2_uri, e13_crm_p106, letter_uri = (
            mkuri(),
            mkuri(),
            mkuri(),
            mkuri(),
        )

        yield from ttl(
            e13_crm_p128_uri,
            (RDF.type, star.E13_crm_P128),
            (crm.P140_assigned_attribute_to, self.correspondence_uri),
            (
                crm.P141_assigned,
                ttl(
                    letter_uri,
                    (RDF.type, r11spec.Letter),
                    (RDFS.label, f"{self.model.letter_sent} (Letter)"),
                ),
            ),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p128_uri)

        # text therein; hashed like in text_publications triples
        text_uri: URIRef = mkuri(f"{self.model.text_therein} - written text")

        yield from ttl(
            e13_crm_p106,
            (RDF.type, star.E13_crm_P106),
            (crm.P140_assigned_attribute_to, letter_uri),
            (
                crm.P141_assigned,
                ttl(
                    text_uri,
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
                (crm.P140_assigned_attribute_to, letter_uri),
                (crm.P141_assigned, person_model.person_uri),
            )

            # authority + passage triples
            yield from self.authority_passage_triples(e13_spec_l2_uri)

    def dispatch_triples(self) -> Iterator[_Triple]:
        e13_crm_p25_uri, dispatch_uri = mkuri(), mkuri()

        yield from ttl(
            e13_crm_p25_uri,
            (RDF.type, star.E13_crm_P25),
            (
                crm.P140_assigned_attribute_to,
                ttl(dispatch_uri, (RDF.type, pwro.WE12_Sending)),
            ),
            (crm.P141_assigned, self.correspondence_uri),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p25_uri)

        # dispatch from
        if (where_sent := self.model.where_sent) is not None:
            e13_pwro_wp13_uri = mkuri()

            yield from ttl(
                e13_pwro_wp13_uri,
                (RDF.type, star.E13_pwro_WP13),
                (crm.P140_assigned_attribute_to, dispatch_uri),
                (
                    crm.P141_assigned,
                    ttl(mkuri(), (RDF.type, crm.E27_Site), (RDFS.label, where_sent)),
                ),
            )

            # authority + passage triples
            yield from self.authority_passage_triples(e13_pwro_wp13_uri)

        # dispatch from to
        if (where_received := self.model.where_received) is not None:
            e13_pwro_wp4_uri = mkuri()

            yield from ttl(
                e13_pwro_wp4_uri,
                (RDF.type, star.E13_pwro_WP9),
                (crm.P140_assigned_attribute_to, dispatch_uri),
                (
                    crm.P141_assigned,
                    ttl(
                        mkuri(), (RDF.type, crm.E27_Site), (RDFS.label, where_received)
                    ),
                ),
            )

            # authority + passage triples
            yield from self.authority_passage_triples(e13_pwro_wp4_uri)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(), self.letter_triples(), self.dispatch_triples()
        )
