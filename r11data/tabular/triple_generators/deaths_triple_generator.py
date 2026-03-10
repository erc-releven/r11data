from collections.abc import Iterable, Iterator
from functools import cached_property

from lodkit import _Triple as Triple, ttl
from r11data.tabular.models import DeathSheetModel
from r11data.tabular.utils.rdf_utils import TripleChain, crm, mkuri, star
from rdflib import RDF, RDFS, URIRef


class DeathsTripleGenerator[TModel: DeathSheetModel](Iterable[Triple]):
    def __init__(self, model: TModel) -> None:
        self.model = model

    @cached_property
    def event_uri(self) -> URIRef:
        return mkuri(str(self.model.person_uri), "Death")

    def base_triples(self) -> Iterator[Triple]:
        event_assertion_uri = mkuri()

        yield from ttl(
            event_assertion_uri,
            (RDF.type, star.E13_crm_P100),
            (
                crm.P140_assigned_attribute_to,
                ttl(self.event_uri, (RDF.type, crm.E69_Death)),
            ),
            (crm.P141_assigned, self.model.person_uri),
        )

        # yield from self.authority_passage_triples(event_assertion_uri)

    def event_description_assertion_triples(self) -> Iterator[Triple]:
        e13_crm_p67_uri = mkuri()

        yield from ttl(
            e13_crm_p67_uri,
            (RDF.type, star.E13_crm_P67),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    mkuri(),
                    (RDF.type, crm.E33_Linguistic_Object),
                    (
                        crm.P190_has_symbolic_content,
                        f"Death of {self.model.name} {self.model.code}.",
                    ),
                ),
            ),
            (crm.P141_assigned, self.event_uri),
        )

        # yield from self.authority_passage_triples(e13_crm_p67_uri)

    def event_date_assertion_triples(self) -> Iterator[Triple]:
        if (date := self.model.date) is None:
            return

        e13_crm_p4_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.event_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri(),
                    (RDF.type, crm["E52_Time-Span"]),
                    (RDFS.label, date),
                ),
            ),
        )

        # yield from self.authority_passage_triples(e13_crm_p4_uri)

    def __iter__(self) -> Iterator[Triple]:
        return TripleChain(
            self.base_triples(),
            self.event_description_assertion_triples(),
            self.event_date_assertion_triples(),
        )
