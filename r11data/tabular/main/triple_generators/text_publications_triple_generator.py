"""TripleGenerator for the Persons sheet."""

from collections.abc import Iterator
from functools import cached_property
import itertools

from lodkit import _Triple, ttl
from r11data.tabular.main.models import TextPublication
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import (
    crm,
    lrm,
    mkuri,
    r11,
    r11pros,
    r11spec,
    star,
)
from rdflib import Literal, RDF, RDFS, URIRef
import structlog


logger = structlog.get_logger()


class TextPublicationsRDFConverter(_ModelRDFConverter[TextPublication]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.written_text_uri: URIRef = mkuri(
            f"{self.model.text_identifier} - written text"
        )
        self.written_text_creation_uri: URIRef = mkuri(
            f"{self.model.text_identifier} - written text creation"
        )
        self.text_edition_uri: URIRef = mkuri(
            f"{self.model.text_identifier} - text edition"
        )
        self.text_edition_creation_uri: URIRef = mkuri(
            f"{self.model.text_identifier} - text edition creation"
        )

    def base_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.written_text_uri,
            (RDF.type, r11spec.Text_Expression),
            (RDFS.label, self.model.text_identifier),
        )

        yield from ttl(
            mkuri(),
            (RDF.type, star.E13_lrmoo_R17),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    self.written_text_creation_uri,
                    (RDF.type, lrm.F28_Expression_Creation),
                ),
            ),
            (crm.P141_assigned, self.written_text_uri),
        )

    def title_assertion_triples(self) -> Iterator[_Triple]:
        if self.model.text_name is None:
            return

        e13_crm_p1_uri = mkuri()

        yield from ttl(
            e13_crm_p1_uri,
            (RDF.type, star.E13_crm_P1),
            (crm.P140_assigned_attribute_to, self.written_text_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri(),
                    (RDF.type, crm.E33_E41_Linguistic_Appellation),
                    (crm.P190_has_symbolic_content, self.model.text_name),
                ),
            ),
        )

        yield from self._p67_source_triples(e13_crm_p1_uri)
        yield from self._p14_authority_triples(e13_crm_p1_uri)

    def creation_time_assertion_triples(self) -> Iterator[_Triple]:
        if self.model.creation_date is None:
            return

        e13_crm_p4_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_p4),
            (crm.P140_assigned_attribute_to, self.written_text_creation_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri(),
                    (RDF.type, crm["E52_Time-Span"]),
                    (RDFS.label, self.model.creation_date),
                ),
            ),
        )

        yield from self._p67_source_triples(e13_crm_p4_uri)
        yield from self._p14_authority_triples(e13_crm_p4_uri)

    def creation_author_assertion_triples(self) -> Iterator[_Triple]:
        if (author := self.model.author) is None:
            return

        e13_crm_p14_uri = mkuri()

        yield from ttl(
            e13_crm_p14_uri,
            (RDF.type, star.E13_crm_P14),
            (crm.P140_assigned_attribute_to, self.written_text_creation_uri),
            (crm.P141_assigned, self.get_person_uri(person_id=author)),
        )

        yield from self._p67_source_triples(e13_crm_p14_uri)
        yield from self._p14_authority_triples(e13_crm_p14_uri)

    def edition_base_triples(self) -> Iterator[_Triple]:
        return ttl(
            self.text_edition_uri,
            (RDF.type, r11spec.Publication),
            (RDFS.label, self.model.edition),  # edition is not optional
        )

    def edition_ceation_assertion_triples(self) -> Iterator[_Triple]:
        return ttl(
            mkuri(),
            (RDF.type, star.E13_lrmoo_R17),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    self.text_edition_creation_uri,
                    (RDF.type, lrm.F28_Expression_Creation),
                ),
            ),
            (crm.P141_assigned, self.text_edition_uri),
        )

    def edition_editor_assertion_triples(self) -> Iterator[_Triple]:
        if (editor_id := self.model.editor) is None:
            return

        editor = self.get_person_uri(editor_id)
        e13_crm_p14_uri = mkuri()

        yield from ttl(
            e13_crm_p14_uri,
            (RDF.type, star.E13_crm_P14),
            (crm.P140_assigned_attribute_at, self.written_text_creation_uri),
            (crm.P141_assigned, editor),
        )

        yield from self._p67_source_triples(e13_crm_p14_uri)
        yield from self._p14_authority_triples(e13_crm_p14_uri)

    def edition_of_text_assertion_triples(self) -> Iterator[_Triple]:
        e13_lrmoo_r76_uri = mkuri()

        yield from ttl(
            e13_lrmoo_r76_uri,
            (RDF.type, star.E13_lrmoo_R76),
            (crm.P140_assigned_attribute_to, self.text_edition_uri),
            (crm.P141_assigned, self.written_text_uri),
        )

        yield from self._p67_source_triples(e13_lrmoo_r76_uri)
        yield from self._p14_authority_triples(e13_lrmoo_r76_uri)

    def _p67_source_triples(self, subject: URIRef) -> Iterator[_Triple]:
        reference = self.model.source_text_reference
        publication = self.model.source_text_publication

        if reference is None and publication is None:
            return

        assert reference is not None
        assert publication is not None

        passage_uri = mkuri(f"{reference} - {publication}")

        yield from ttl(
            passage_uri,
            (RDF.type, crm.E33_Linguistic_Object),
            (RDFS.label, reference),
            (crm.P67_refers_to, subject),
        )

        if (excerpt := self.model.source_text_excerpt) is not None:
            yield (
                passage_uri,
                crm.P190_has_symbolic_content,
                Literal(excerpt),
            )

    def _p14_authority_triples(self, subject: URIRef) -> Iterator[_Triple]:
        if (authority_data := self.authority_data) is None:
            return
        authority_uri, _ = authority_data
        yield (subject, crm.P14_carried_out_by, authority_uri)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.title_assertion_triples(),
            self.creation_time_assertion_triples(),
            self.creation_author_assertion_triples(),
            self.edition_base_triples(),
        )
