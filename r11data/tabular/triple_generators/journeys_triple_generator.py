"""TripleGenerator for the Journeys sheet."""

import itertools
from collections.abc import Iterable, Iterator

from lodkit import _Triple, ttl
from r11data.tabular.models import AuthorityStatus, Journey, Person, Place
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.rdf_utils import (
    crm,
    generate_time_triples,
    mkuri,
    pwro,
    star,
)
from rdflib import RDF, URIRef


class JourneysRDFConverter(_ModelRDFConverter[Journey]):
    def base_triples(self) -> Iterable[_Triple]:
        return ttl(
            self.model.voyage_uri,
            (RDF.type, pwro.WE7_Voyage),
        )

    def journey_undertaken_assertion_triples(self) -> Iterable[_Triple]:
        if (who_travelled := self.model.who_travelled) is None:
            return

        who_travelled_model: Person | None = self.get_person_data(
            who_travelled, strict=False
        )

        if who_travelled_model is None:
            return

        e13_pwro_wp7_uri = mkuri()

        yield from ttl(
            e13_pwro_wp7_uri,
            (RDF.type, star.E13_pwro_WP7),
            (crm.P140_assigned_attribute_to, self.model.voyage_uri),
            (crm.P141_assigned, who_travelled_model.person_uri),
        )

        yield from self.authority_passage_triples(e13_pwro_wp7_uri)

    def journey_time_frame_assertion_triples(self) -> Iterable[_Triple]:
        """Time-Spans currently based start dates;
        the tables have data like start_date='J 1000', end_data='J 1000 - J 1001'
        and it is not entirely clear how to exactly translate that to CRM.
        """

        if (start_date := self.model.start_date) is None:
            return

        e13_crm_p4_uri = mkuri()
        e52_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.model.voyage_uri),
            (crm.P141_assigned, e52_uri),
        )

        yield from generate_time_triples(e52_uri, start_date)
        yield from self.authority_passage_triples(e13_crm_p4_uri)

    def journey_under_authority_assertion_triples(self) -> Iterable[_Triple]:
        if (sent_by_person := self.model.sent_by_person) is None:
            return

        authority_model: AuthorityStatus | None = self.lookup(
            sheet=self.sheets.authority_status,
            model=AuthorityStatus,
            column="Authority ascribed",
            key=sent_by_person,
            strict=False,
        )

        if authority_model is None:
            return

        e13_aaao_zp75_uri = mkuri()

        yield from ttl(
            e13_aaao_zp75_uri,
            (RDF.type, star.E13_aaao_ZP75),
            (crm.P140_assigned_attribute_to, authority_model.status_uri),
            (crm.P141_assigned, self.model.voyage_uri),
        )

        yield from self.authority_passage_triples(e13_aaao_zp75_uri)

    ##################################################
    #### des./real Origin/Destination; lots of duplication here -> refactor

    def designated_origin_assertion_triples(self) -> Iterable[_Triple]:
        if (des_origin := self.model.des_origin) is None:
            return

        des_origin_place_model: Place | None = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=des_origin,
            strict=False,
        )

        if des_origin_place_model is None:
            return

        e13_pwro_wp13_uri = mkuri()

        yield from ttl(
            e13_pwro_wp13_uri,
            (RDF.type, star.E13_pwro_WP13),
            (crm.P140_assigned_attribute_to, self.model.voyage_uri),
            (crm.P141_assigned, des_origin_place_model.place_uri),
        )

        yield from self.authority_passage_triples(e13_pwro_wp13_uri)

    def designated_destination_assertion_triples(self) -> Iterable[_Triple]:
        if (des_destination := self.model.des_destination) is None:
            return

        des_destination_place_model: Place | None = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=des_destination,
            strict=False,
        )

        if des_destination_place_model is None:
            return

        e13_pwro_WP9 = mkuri()

        yield from ttl(
            e13_pwro_WP9,
            (RDF.type, star.E13_pwro_WP9),
            (crm.P140_assigned_attribute_to, self.model.voyage_uri),
            (crm.P141_assigned, des_destination_place_model.place_uri),
        )

        yield from self.authority_passage_triples(e13_pwro_WP9)

    def real_origin_assertion_triples(self) -> Iterable[_Triple]:
        if (real_origin := self.model.real_origin) is None:
            return

        real_origin_place_model: Place | None = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=real_origin,
            strict=False,
        )

        if real_origin_place_model is None:
            return

        e13_crm_p27_uri = mkuri()

        yield from ttl(
            e13_crm_p27_uri,
            (RDF.type, star.E13_crm_P27),
            (crm.P140_assigned_attribute_to, self.model.voyage_uri),
            (crm.P141_assigned, real_origin_place_model.place_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p27_uri)

    def real_destination_assertion_triples(self) -> Iterable[_Triple]:
        if (real_destination := self.model.real_destination) is None:
            return

        real_destination_place_model: Place | None = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=real_destination,
            strict=False,
        )

        if real_destination_place_model is None:
            return

        e13_crm_p26_uri = mkuri()

        yield from ttl(
            e13_crm_p26_uri,
            (RDF.type, star.E13_crm_P26),
            (crm.P140_assigned_attribute_to, self.model.voyage_uri),
            (crm.P141_assigned, real_destination_place_model.place_uri),
        )

    ##################################################

    #### Visit assertions
    def visit_assertion_triples(self) -> Iterable[_Triple]:
        e13_crm_p9_uri = mkuri()

        yield from ttl(
            e13_crm_p9_uri,
            (RDF.type, star.E13_crm_P9),
            (crm.P140_assigned_attribute_to, self.model.voyage_uri),
            (
                crm.P141_assigned,
                ttl(self.model.visit_uri, (RDF.type, pwro.WE13_Visit)),
            ),
        )

        yield from self.authority_passage_triples(e13_crm_p9_uri)

    def visit_time_frame_assertion_triples(self) -> Iterable[_Triple]:
        if (visited_when := self.model.visited_when) is None:
            return

        e13_crm_p4_uri = mkuri()
        e52_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.model.visit_uri),
            (crm.P141_assigned, ttl(e52_uri, (RDF.type, crm["E52_Time-Span"]))),
        )

        yield from generate_time_triples(e52_uri=e52_uri, date_value=visited_when)
        yield from self.authority_passage_triples(e13_crm_p4_uri)

    def visited_place_assertion_triples(self) -> Iterable[_Triple]:
        if (visited_place := self.model.visited_place) is None:
            return

        visited_place_model: Place | None = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=visited_place,
            strict=False,
        )

        if visited_place_model is None:
            return

        e13_pwro_wp14_uri = mkuri()

        yield from ttl(
            e13_pwro_wp14_uri,
            (RDF.type, star.E13_pwro_WP14),
            (crm.P140_assigned_attribute_to, self.model.visit_uri),
            (crm.P141_assigned, visited_place_model.place_uri),
        )

        yield from self.authority_passage_triples(e13_pwro_wp14_uri)

    def visited_person_assertion(self) -> Iterable[_Triple]:
        if (visited_person := self.model.visited_person) is None:
            return

        person_model: Person | None = self.get_person_data(
            person_id=visited_person, strict=False
        )
        if person_model is None:
            return

        e13_crm_p14_uri = mkuri()

        yield from ttl(
            e13_crm_p14_uri,
            (RDF.type, star.E13_crm_P14),
            (crm.P140_assigned_attribute_to, self.model.visit_uri),
            (crm.P141_assigned, person_model.person_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p14_uri)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.journey_undertaken_assertion_triples(),
            self.journey_time_frame_assertion_triples(),
            self.journey_under_authority_assertion_triples(),
            # origin/destination
            self.designated_origin_assertion_triples(),
            self.designated_destination_assertion_triples(),
            self.real_origin_assertion_triples(),
            self.real_destination_assertion_triples(),
            # visit assertions
            self.visit_assertion_triples(),
            self.visit_time_frame_assertion_triples(),
            self.visited_place_assertion_triples(),
            self.visited_person_assertion(),
        )
