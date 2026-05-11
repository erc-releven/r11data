"""TripleGenerator for the Births and deaths sheet."""

import itertools
from collections.abc import Iterator
from functools import cached_property

from lodkit import _Triple, ttl
from r11data.tabular.models import BirthAndDeath, Person, Place
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.date_parser import generate_date_triples
from r11data.tabular.utils.rdf_utils import crm, mkuri, star
from rdflib import RDF, RDFS, URIRef


class BirthDeathEventRDFConverter(_ModelRDFConverter[BirthAndDeath]):
    @cached_property
    def person_model(self) -> Person:
        return self.get_person_data(self.model.who, strict=True)

    @cached_property
    def person_uri(self) -> URIRef:
        return self.person_model.person_uri

    @cached_property
    def event_uri(self) -> URIRef:
        return mkuri(self.person_uri, self.model.which)

    def base_triples(self) -> Iterator[_Triple]:
        event_assertion_uri = mkuri()

        match self.model.which:
            case "Birth":
                event_class, event_assertion_class = crm.E67_Birth, star.E13_crm_P98
            case "Death":
                event_class, event_assertion_class = crm.E69_Death, star.E13_crm_P100
            case _:
                raise ValueError("Event must be 'Birth' or 'Death'.")

        yield from ttl(
            event_assertion_uri,
            (RDF.type, event_assertion_class),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    self.event_uri,
                    (RDF.type, event_class),
                    (
                        RDFS.label,
                        f"{self.model.which} of {self.person_model.descriptive_name}.",
                    ),
                ),
            ),
            (crm.P141_assigned, self.person_uri),
        )

        yield from self.authority_passage_triples(event_assertion_uri)

    def event_date_assertion_triples(self) -> Iterator[_Triple]:
        if (date := self.model.when) is None:
            return

        e13_crm_p4_uri = mkuri()
        e52_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.event_uri),
            (
                crm.P141_assigned,
                ttl(
                    e52_uri,
                    (RDF.type, crm["E52_Time-Span"]),
                ),
            ),
        )

        yield from generate_date_triples(e52_uri, date)
        yield from self.authority_passage_triples(e13_crm_p4_uri)

    def event_place_assertion_triples(self) -> Iterator[_Triple]:
        if (place := self.model.where) is None:
            return

        e13_crm_p7_uri = mkuri()
        place_model: Place = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=place,
            strict=True,
        )

        yield from ttl(
            e13_crm_p7_uri,
            (RDF.type, star.E13_crm_P7),
            (crm.P140_assigned_attribute_to, self.event_uri),
            (crm.P141_assigned, ttl(place_model.place_uri, (RDF.type, crm.E27_Site))),
        )

        yield from self.authority_passage_triples(e13_crm_p7_uri)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.event_date_assertion_triples(),
            self.event_place_assertion_triples(),
        )
