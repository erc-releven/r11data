"""TripleGenerator for the Persons sheet."""

from collections.abc import Iterator
from functools import cached_property
import itertools

from rdflib import Literal, RDF, RDFS, URIRef

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
import structlog


logger = structlog.get_logger()


class TextPublicationsRDFConverter(_ModelRDFConverter[TextPublication]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.written_text_uri: URIRef = self._mktexturi("written text")
        self.written_text_creation_uri: URIRef = self._mktexturi(
            "written text creation"
        )
        self.text_edition_uri: URIRef = self._mktexturi("text edition")
        self.text_edition_creation_uri: URIRef = self._mktexturi(
            "text edition creation"
        )

    def _mktexturi(self, hash_part: str) -> URIRef:
        """Helpter for creating a text_identifier based hashed URI."""
        return mkuri(f"{self.model.text_identifier} - {hash_part}")

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
        if (text_name := self.model.text_name) is None:
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
                    (crm.P190_has_symbolic_content, text_name),
                ),
            ),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p1_uri)

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

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p4_uri)

    def creation_author_assertion_triples(self) -> Iterator[_Triple]:
        if (author := self.model.author) is None:
            return
        if (person := self.get_person_uri(author, strict=False)) is None:
            return

        e13_crm_p14_uri = mkuri()

        yield from ttl(
            e13_crm_p14_uri,
            (RDF.type, star.E13_crm_P14),
            (crm.P140_assigned_attribute_to, self.written_text_creation_uri),
            # (crm.P141_assigned, self.get_person_uri(person_id=author)),
            (crm.P141_assigned, person),
        )
        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p14_uri)

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
        if (editor := self.get_person_uri(editor_id, strict=False)) is None:
            return

        e13_crm_p14_uri = mkuri()

        yield from ttl(
            e13_crm_p14_uri,
            (RDF.type, star.E13_crm_P14),
            (crm.P140_assigned_attribute_to, self.written_text_creation_uri),
            (crm.P141_assigned, editor),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p14_uri)

    def edition_of_text_assertion_triples(self) -> Iterator[_Triple]:
        e13_lrmoo_r76_uri = mkuri()

        yield from ttl(
            e13_lrmoo_r76_uri,
            (RDF.type, star.E13_lrmoo_R76),
            (crm.P140_assigned_attribute_to, self.text_edition_uri),
            (crm.P141_assigned, self.written_text_uri),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_lrmoo_r76_uri)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.title_assertion_triples(),
            self.creation_time_assertion_triples(),
            self.creation_author_assertion_triples(),
            self.edition_base_triples(),
            self.edition_ceation_assertion_triples(),
            self.edition_editor_assertion_triples(),
            self.edition_of_text_assertion_triples(),
        )
