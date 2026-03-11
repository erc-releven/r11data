from collections.abc import Iterable, Iterator
from hashlib import sha256
import itertools
import logging
from typing import Literal as TypingLiteral, Self
from uuid import uuid4
import warnings

from lodkit import ClosedOntologyNamespace, NamespaceGraph, _Triple as Triple
from r11data.tabular.utils.date_parser import R11DateParser
from r11data.utils.paths import ontologies_path
from rdflib import Graph, Literal, Namespace, RDFS, URIRef


logger = logging.getLogger(__name__)


class URIConstructorFactory:
    def __init__(
        self,
        namespace: str,
    ) -> None:
        self.namespace = Namespace(namespace)

    def __call__(self, *hash_values: str) -> URIRef:
        if not hash_values:
            segment = str(uuid4())
            return self.namespace[segment]

        _hash_values: Iterable[str] = map(lambda x: x.strip().lower(), hash_values)
        hash_value: bytes = " / ".join(_hash_values).encode("utf8")

        digest = sha256(hash_value).hexdigest()
        segment = digest[:36]

        return self.namespace[segment]


crm = ClosedOntologyNamespace(ontology=ontologies_path / "crm.ttl")
crmdig = ClosedOntologyNamespace(ontology=ontologies_path / "crmdig.ttl")
lrm = ClosedOntologyNamespace(ontology=ontologies_path / "lrmoo.ttl")

r11 = Namespace("https://r11.eu/rdf/resource/")
star = Namespace("https://r11.eu/ns/star/")
r11spec = Namespace("https://r11.eu/ns/spec/")
r11pros = Namespace("https://r11.eu/ns/prosopography/")
pwro = Namespace("https://ontology.swissartresearch.net/pwro/")

aaao = Namespace("https://ontology.swissartresearch.net/aaao/")
so = Namespace("https://r11.eu/ns/similarity/")

mkuri = URIConstructorFactory(r11)

tara_uri = mkuri("0000-0001-6930-3470")
lewis_uri = mkuri("0009-0007-3535-6823")
aleks_uri = mkuri("0009-0007-1432-0127")
marton_uri = mkuri("0000-0003-3547-0750")


class RelevenGraph(NamespaceGraph):
    crmdig = crmdig
    crm = crm

    r11 = r11
    star = star
    r11spec = r11spec
    r11pros = r11pros


def get_source_name_lang_tag(
    source_name: str,
) -> TypingLiteral["xcl", "grc", "ar"] | None:
    code = ord(source_name[0])

    match code:
        case c if 0x0530 <= c <= 0x058F:
            return "xcl"
        case c if 0x0370 <= c <= 0x03FF or 0x1F00 <= c <= 0x1FFF:
            return "grc"
        case c if (
            0x0600 <= c <= 0x06FF or 0x0750 <= c <= 0x077F or 0x08A0 <= c <= 0x08FF
        ):
            return "ar"
        case _:
            return None


class TripleChain(itertools.chain[Triple]):
    """A simple itertools.chain for chaining lodkit._Triple iterables.

    TripleChain implements a fluid chain interface,
    i.e TripleChain objects can be chained repeatedly.

    TripleChain also exposes a to_graph method that generates a Graph
    from the triples stored in the TripleChain.
    Note that calling to_graph exhausts the TripleChain object.
    """

    def chain(self, *others: Iterable[Triple]) -> Self:
        return self.__class__(self, *others)

    def to_graph(self: Iterable[Triple], graph: Graph | None = None) -> Graph:
        _graph: Graph = Graph() if graph is None else graph

        for triple in self:
            _graph.add(triple)

        if not _graph:
            msg = f"Graph object '{_graph}' is empty. This might indicate an exhausted iterator."
            warnings.warn(msg)

        return _graph


def _generate_julian_day_triples(
    e52_uri: URIRef, parsed_date: R11DateParser
) -> Iterator[Triple]:
    """Logic for creating time triples based on an R11DateParser object.

    -- cases --
    1. position (begin == end):
    2. duration (begin != end)
    3 position/known_limit
      3.1 TAQ position
      3.2 TPQ position
    4 duration/known_limit
      4.1 TAQ duration
      4.2 TPQ duration
    """
    jd_begin, jd_end = parsed_date.jd_duration
    is_position: bool = jd_begin == jd_end
    known_limit = parsed_date.date_entry.known_limit

    jd = r11["JulianDay"]

    match is_position, known_limit:
        case True, None:
            yield (
                e52_uri,
                crm["P82_at_some_time_within"],
                Literal(jd_begin, datatype=jd),
            )
        case True, "TAQ":
            # end of the end
            yield (e52_uri, crm["P82b_end_of_the_end"], Literal(jd_begin, datatype=jd))
        case True, "TPQ":
            # begin of the begin
            yield (
                e52_uri,
                crm["P82a_begin_of_the_begin"],
                Literal(jd_begin, datatype=jd),
            )
        case False, None:
            yield from [
                (
                    e52_uri,
                    crm["P82a_begin_of_the_begin"],
                    Literal(jd_begin, datatype=jd),
                ),
                (e52_uri, crm["P82b_end_of_the_end"], Literal(jd_end, datatype=jd)),
            ]
        case False, "TAQ":
            yield from [
                (e52_uri, crm["P81b_begin_of_the_end"], Literal(jd_begin, datatype=jd)),
                (e52_uri, crm["P82b_end_of_the_end"], Literal(jd_end, datatype=jd)),
            ]
        case False, "TPQ":
            # begin of the begin, end of the begin
            yield from [
                (
                    e52_uri,
                    crm["P82a_begin_of_the_begin"],
                    Literal(jd_begin, datatype=jd),
                ),
                (e52_uri, crm["P81a_end_of_the_begin"], Literal(jd_end, datatype=jd)),
            ]
        case _:
            raise Exception("Time triple switch failed.")


def generate_time_triples(e52_uri: URIRef, date_value: str | None) -> Iterator[Triple]:
    """Triple generator for generating temporal assertions given an  E52 URI and a date value string.

    If the date value string can be parsed into a R11DateParser object,
    the generator will yield temporal CRM assertions with JulianDay-converted dates;
    else, the generator will simply yield an rdfs:label label assertion for the date string.
    """
    if date_value is not None:
        yield (e52_uri, RDFS.label, Literal(date_value))

        try:
            parsed_date = R11DateParser(date_value=date_value)
        except Exception:
            msg = f"Failed to parse death date value '{date_value}'."
            logger.warning(msg)
        else:
            yield from _generate_julian_day_triples(
                e52_uri=e52_uri, parsed_date=parsed_date
            )
