from collections.abc import Iterable, Iterator
from functools import cached_property
import logging

from lodkit import _Triple as Triple, ttl
from r11data.tabular.models import DeathSheetModel
from r11data.tabular.utils.rdf_utils import crm, generate_time_triples, mkuri, star
from rdflib import RDF, URIRef


logger = logging.getLogger(__name__)


class DeathsTripleGenerator[TModel: DeathSheetModel](Iterable[Triple]):
    def __init__(self, model: TModel) -> None:
        self.model = model

    @cached_property
    def death_event_uri(self) -> URIRef:
        return mkuri(self.model.person_uri, "Death")

    def __iter__(self) -> Iterator[Triple]:
        e13_crm_p4_uri = mkuri()
        e52_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.death_event_uri),
            (
                crm.P141_assigned,
                e52_uri,
            ),
        )

        # time assertions
        yield from generate_time_triples(e52_uri=e52_uri, date_value=self.model.date)

        # p14/p67
