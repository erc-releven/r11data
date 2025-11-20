"""TripleGenerator for the Manuscripts sheet."""

from collections.abc import Iterable, Iterator
import itertools

from lodkit import _Triple, ttl
from r11data.tabular.main.models import Manuscript, Person, TextPublication
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import crm, mkuri, r11spec, star
from rdflib import RDF, RDFS
import structlog


logger = structlog.get_logger()


class ManuscriptRDFConverter(_ModelRDFConverter[Manuscript]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.manuscript_uri = mkuri(self.model.identifier)
        self.manuscript_production_uri = mkuri(
            f"{self.model.identifier} - manuscript production"
        )

    def base_triples(self) -> Iterable[_Triple]:
        return ttl(
            self.manuscript_uri,
            (RDF.type, r11spec.Manuscript),
            (RDFS.label, self.model.identifier),
        )

    def manuscript_assertion_triples(self) -> Iterable[_Triple]:
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
            (crm.P140_assigned_attribute_to, self.manuscript_uri),
            (crm.P141_assigned, contained_publication.text_identifier),
        )

        yield from self.authority_passage_triples(e13_crm_128_uri)

    def manuscript_production_triples(self) -> Iterable[_Triple]:
        e13_crm_p108 = mkuri()

        yield from ttl(
            e13_crm_p108,
            (RDF.type, star.E13_crm_P108),
            (
                crm.P140_assigned_attribute_to,
                ttl(self.manuscript_production_uri, (RDF.type, crm.E12_Production)),
            ),
            (crm.P141_assigned, self.manuscript_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p108)

    # B dating
    def manuscript_timeframe_assertion(self) -> Iterable[_Triple]:
        e13_crm_p4_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.manuscript_production_uri),
            # note: this might be translated to Julian date;
            # however, the Wisskas query is currently asking only about the label
            (
                crm.P141_assigned,
                ttl(
                    mkuri(),
                    (RDF.type, crm["E52_Time-Span"]),
                    (RDFS.label, self.model.dating),
                ),
            ),
        )

        yield from self.authority_passage_triples(e13_crm_p4_uri)

    # C place copied
    def manuscript_location_assertion(self) -> Iterable[_Triple]:
        if (place := self.model.place_copied) is None:
            return

        e13_crm_p7_uri = mkuri()

        yield from ttl(
            e13_crm_p7_uri,
            (RDF.type, star.E13_crm_P7),
            (crm.P140_assigned_attribute_to, self.manuscript_production_uri),
            (
                crm.P141_assigned,
                ttl(mkuri(), (RDF.type, crm.E27_Site), (RDFS.label, place)),
            ),
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
            (crm.P140_assigned_attribute_to, self.manuscript_production_uri),
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
            (crm.P140_assigned_attribute_to, self.manuscript_production_uri),
            (crm.P141_assigned, person_model.person_uri),
        )

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.manuscript_assertion_triples(),
            self.manuscript_production_triples(),
            self.manuscript_timeframe_assertion(),
            self.manuscript_location_assertion(),
            self.manuscript_scribe_assertion(),
            self.manuscript_commissioner_assertion(),
        )
