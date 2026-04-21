import itertools
import logging
import warnings
from collections.abc import Iterable, Iterator
from hashlib import sha256
from pathlib import PurePath
from types import MappingProxyType
from typing import IO, Self, TextIO
from typing import Literal as TypingLiteral
from uuid import uuid4

from lodkit import NamespaceGraph
from lodkit import _Triple as Triple
from r11data.tabular.utils.date_parser import R11DateParser
from r11data.utils.paths import ontologies_path
from rdflib import RDFS, Graph, Literal, Namespace, URIRef
from rdflib.parser import InputSource
from rdflib.query import Result

logger = logging.getLogger(__name__)


type GraphParseSource = IO[bytes] | TextIO | InputSource | str | bytes | PurePath
"""Source parameter type for rdflib.Graph.parse."""


class NoSolutionException(Exception): ...


class EmptySolutionException(Exception): ...  # pragma: no cover


class ClosedOntologyNamespace:
    """Ontology-based Namespace constructor.

    ClosedOntologyNamespace allows constructing a namespace
    based on an Ontology or generally an RDF graph source.

    Given a lodkit.types.GraphParseSource or an rdflib.Graph,
    the source is queried for RDF class and property definition assertions.
    RDF term names are extracted by splitting the last IRI segment delimited by
    '#', '/' or ':' and  matching name/IRI pairs are registered in the namespace mapping.

    Namespace members are accessible as both attributes and items of a given
    `ClosedOntologyNamespace` instance, i.e. attribute and item access is routed
    to `ClosedOntologyNamespace.mapping`. For dictionary operations over the namespace mapping,
    the public `ClosedOntologyNamespace.mapping` can be accessed directly.

    In the case of RDF term names conflicting with class namespace names,
    the class namespace names take precedence for attribute access;
    conflicting RDF terms are still accessible via item lookup
    or through the `ClosedOntologyNamespace.mapping` proxy.

    """

    _query = """
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix owl: <http://www.w3.org/2002/07/owl#>

    select distinct ?name ?uri
    where {
    values ?type {
      rdfs:Class
      owl:Class

      rdf:Property
      owl:ObjectProperty
      owl:DatatypeProperty
      owl:AnnotationProperty

      owl:NamedIndividual
    }

    ?uri a ?type .
    filter (isIRI(?uri))

    bind (replace(str(?uri), "^.*[#/:]", "") AS ?name)
    filter (?name != "")
    }
    """

    def __init__(self, source: GraphParseSource | Graph, *parse_args, **parse_kwargs):
        self.source = source

        graph: Graph = (
            self.source
            if isinstance(self.source, Graph)
            else Graph().parse(source=self.source, *parse_args, **parse_kwargs)
        )
        sparql_result: Result = graph.query(self._query)

        self.mapping: MappingProxyType[str, URIRef] = self._get_uris(
            sparql_result=sparql_result
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} source={self.source!r}>"

    def __getattr__(self, value):
        return self[value]

    def __getitem__(self, key: str) -> URIRef:
        try:
            return self.mapping[key]
        except KeyError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'."
            )

    def _get_uris(self, sparql_result: Result) -> MappingProxyType[str, URIRef]:
        _bindings = sparql_result.bindings

        match _bindings:
            case []:
                raise NoSolutionException()
            case [{**items}] if not items:  # pragma: no cover (unreachable)
                raise EmptySolutionException()
            case _:
                return MappingProxyType(
                    {
                        str(binding["name"]): binding["uri"]  # type: ignore
                        for binding in _bindings
                    }
                )


crm = ClosedOntologyNamespace(source=ontologies_path / "crm.ttl")
crmdig = ClosedOntologyNamespace(source=ontologies_path / "crmdig.ttl")
lrm = ClosedOntologyNamespace(source=ontologies_path / "lrmoo.ttl")

star = ClosedOntologyNamespace(source=ontologies_path / "star.ttl")
r11spec = ClosedOntologyNamespace(source=ontologies_path / "r11spec.ttl")
r11pros = ClosedOntologyNamespace(source=ontologies_path / "r11pros.ttl")
pwro = ClosedOntologyNamespace(source=ontologies_path / "pwro.ttl")

aaao = ClosedOntologyNamespace(source=ontologies_path / "aaao.ttl")
so = ClosedOntologyNamespace(source=ontologies_path / "so.ttl")

r11 = Namespace("https://r11.eu/rdf/resource/")


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


mkuri = URIConstructorFactory(r11)

tara_uri = mkuri("0000-0001-6930-3470")
lewis_uri = mkuri("0009-0007-3535-6823")
aleks_uri = mkuri("0009-0007-1432-0127")
marton_uri = mkuri("0000-0003-3547-0750")


class RelevenGraph(NamespaceGraph): ...


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
            msg = f"Failed to parse date value '{date_value}'."
            logger.warning(msg)
        else:
            yield from _generate_julian_day_triples(
                e52_uri=e52_uri, parsed_date=parsed_date
            )
