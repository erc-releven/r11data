"""TripleGenerator for the Manuscripts sheet."""

import itertools
from collections.abc import Iterable, Iterator

from lodkit import _Triple, ttl
from r11data.tabular.models import Manuscript, Person, Place, TextPublication
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.rdf_utils import (
    crm,
    generate_time_triples,
    mkuri,
    r11spec,
    star,
)
from rdflib import RDF, RDFS


class ManuscriptRDFConverter(_ModelRDFConverter[Manuscript]):
    def base_triples(self) -> Iterable[_Triple]:
        return ttl(
            self.model.manuscript_uri,
            (RDF.type, r11spec.Manuscript),
            (RDFS.label, self.model.identifier),
        )

    def manuscript_contains_text_triples(self) -> Iterable[_Triple]:
        contained_publication: TextPublication | None = self.lookup(
            sheet=self.sheets.text_publications,
            model=TextPublication,
            column="Text identifier",
            key=self.model.contains_text,
            strict=False,
        )

        if contained_publication is None:
            return

        e13_crm_128_uri = mkuri()

        yield from ttl(
            e13_crm_128_uri,
            (RDF.type, star.E13_crm_P128),
            (crm.P140_assigned_attribute_to, self.model.manuscript_uri),
            (crm.P141_assigned, contained_publication.text_identifier),
        )

        yield from self.authority_passage_triples(e13_crm_128_uri)

    def manuscript_production_triples(self) -> Iterable[_Triple]:
        e13_crm_p108_uri = mkuri()

        yield from ttl(
            e13_crm_p108_uri,
            (RDF.type, star.E13_crm_P108),
            (crm.P141_assigned, self.model.manuscript_uri),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    self.model.manuscript_production_uri, (RDF.type, crm.E12_Production)
                ),
            ),
        )

        yield from self.authority_passage_triples(e13_crm_p108_uri)

    def manuscript_timeframe_assertion(self) -> Iterable[_Triple]:
        e13_crm_p4_uri = mkuri()
        e52_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.model.manuscript_production_uri),
            (
                crm.P141_assigned,
                ttl(
                    e52_uri,
                    (RDF.type, crm["E52_Time-Span"]),
                    (RDFS.label, self.model.dating),
                ),
            ),
        )

        yield from generate_time_triples(e52_uri=e52_uri, date_value=self.model.dating)
        yield from self.authority_passage_triples(e13_crm_p4_uri)

    def manuscript_location_assertion(self) -> Iterable[_Triple]:
        if (place := self.model.place_copied) is None:
            return

        place_model: Place | None = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=place,
            strict=False,
        )

        if place_model is None:
            return

        e13_crm_p7_uri = mkuri()

        yield from ttl(
            e13_crm_p7_uri,
            (RDF.type, star.E13_crm_P7),
            (crm.P140_assigned_attribute_to, self.model.manuscript_production_uri),
            (crm.P141_assigned, place_model.place_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p7_uri)

    # E scribe
    def manuscript_scribe_assertion(self) -> Iterable[_Triple]:
        person_model: Person | None = self.get_person_data(
            self.model.scribe, strict=False
        )
        if person_model is None:
            return

        e13_crm_p14_uri = mkuri()

        yield from ttl(
            e13_crm_p14_uri,
            (RDF.type, star.E13_crm_P14),
            (crm.P140_assigned_attribute_to, self.model.manuscript_production_uri),
            (crm.P141_assigned, person_model.person_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p14_uri)

    # F commissioner
    def manuscript_commissioner_assertion(self) -> Iterable[_Triple]:
        if (commissioner := self.model.commissioned_by) is None:
            return
        if (person_model := self.get_person_data(commissioner, strict=False)) is None:
            return

        e13_crm_p11_uri = mkuri()

        yield from ttl(
            e13_crm_p11_uri,
            (RDF.type, star.E13_crm_P11),
            (crm.P140_assigned_attribute_to, self.model.manuscript_production_uri),
            (crm.P141_assigned, person_model.person_uri),
        )

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.manuscript_contains_text_triples(),
            self.manuscript_production_triples(),
            self.manuscript_timeframe_assertion(),
            self.manuscript_location_assertion(),
            self.manuscript_scribe_assertion(),
            self.manuscript_commissioner_assertion(),
        )
