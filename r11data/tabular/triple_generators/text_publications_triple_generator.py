"""TripleGenerator for the Persons sheet."""

import itertools
from collections.abc import Iterator

from lodkit import _Triple, ttl
from r11data.tabular.models import TextPublication
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.rdf_utils import (
    crm,
    generate_time_triples,
    lrm,
    mkuri,
    r11spec,
    star,
)
from rdflib import RDF, RDFS


class TextPublicationsRDFConverter(_ModelRDFConverter[TextPublication]):
    """RDFConverter for TextPublication models.

    Note: Here, the Authority data is always the same as the TextPublication data;
    i.e. assertions about TextPublications have themselves as authority.
    """

    def base_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.model.text_expression_uri,
            (RDF.type, r11spec.Text_Expression),
            (RDFS.label, self.model.text_identifier),
        )

        yield from ttl(
            mkuri(),
            (RDF.type, star.E13_lrmoo_R17),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    self.model.text_expression_creation_uri,
                    (RDF.type, lrm.F28_Expression_Creation),
                ),
            ),
            (crm.P141_assigned, self.model.text_expression_uri),
        )

    def title_assertion_triples(self) -> Iterator[_Triple]:
        if (text_name := self.model.text_name) is None:
            return

        e13_crm_p1_uri = mkuri()

        yield from ttl(
            e13_crm_p1_uri,
            (RDF.type, star.E13_crm_P1),
            (crm.P140_assigned_attribute_to, self.model.text_expression_uri),
            (
                crm.P141_assigned,
                ttl(
                    self.model.text_expression_appellation_uri,
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
        e52_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.model.text_expression_creation_uri),
            (
                crm.P141_assigned,
                ttl(
                    e52_uri,
                    (RDF.type, crm["E52_Time-Span"]),
                    (RDFS.label, self.model.creation_date),
                ),
            ),
        )

        yield from generate_time_triples(
            e52_uri=e52_uri, date_value=self.model.creation_date
        )
        yield from self.authority_passage_triples(e13_crm_p4_uri)

    def creation_author_assertion_triples(self) -> Iterator[_Triple]:
        if (author := self.model.author) is None:
            return
        if (person_data := self.get_person_data(author, strict=False)) is None:
            return

        e13_crm_p14_uri = mkuri()

        yield from ttl(
            e13_crm_p14_uri,
            (RDF.type, star.E13_crm_P14),
            (crm.P140_assigned_attribute_to, self.model.text_expression_creation_uri),
            (crm.P141_assigned, person_data.person_uri),
        )
        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p14_uri)

    def edition_base_triples(self) -> Iterator[_Triple]:
        return ttl(
            self.model.text_publication_uri,
            (RDF.type, r11spec.Publication),
            (RDFS.label, self.model.edition),
        )

    def edition_ceation_assertion_triples(self) -> Iterator[_Triple]:
        return ttl(
            mkuri(),
            (RDF.type, star.E13_lrmoo_R17),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    self.model.text_publication_creation_uri,
                    (RDF.type, lrm.F28_Expression_Creation),
                ),
            ),
            (crm.P141_assigned, self.model.text_publication_uri),
        )

    def edition_editor_assertion_triples(self) -> Iterator[_Triple]:
        if (editor_id := self.model.editor) is None:
            return
        if (person_data := self.get_person_data(editor_id, strict=False)) is None:
            return

        e13_crm_p14_uri = mkuri()

        yield from ttl(
            e13_crm_p14_uri,
            (RDF.type, star.E13_crm_P14),
            (crm.P140_assigned_attribute_to, self.model.text_publication_creation_uri),
            (crm.P141_assigned, person_data.person_uri),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p14_uri)

    def edition_of_text_assertion_triples(self) -> Iterator[_Triple]:
        e13_lrmoo_r76_uri = mkuri()

        yield from ttl(
            e13_lrmoo_r76_uri,
            (RDF.type, star.E13_lrmoo_R76),
            (crm.P140_assigned_attribute_to, self.model.text_publication_uri),
            (crm.P141_assigned, self.model.text_expression_uri),
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
