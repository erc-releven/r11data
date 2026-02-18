from collections.abc import Iterable
from hashlib import sha256
import itertools
from typing import Literal as TypingLiteral, Self
from uuid import uuid4
import warnings

from lodkit import ClosedOntologyNamespace, NamespaceGraph, _Triple
from r11data.utils.paths import ontologies_path
from rdflib import Graph, Namespace, Namespace, URIRef


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


class TripleChain(itertools.chain[_Triple]):
    """A simple itertools.chain for chaining lodkit._Triple iterables.

    TripleChain implements a fluid chain interface,
    i.e TripleChain objects can be chained repeatedly.

    TripleChain also exposes a to_graph method that generates a Graph
    from the triples stored in the TripleChain.
    Note that calling to_graph exhausts the TripleChain object.
    """

    def chain(self, *others: Iterable[_Triple]) -> Self:
        return self.__class__(self, *others)

    def to_graph(self: Iterable[_Triple], graph: Graph | None = None) -> Graph:
        _graph: Graph = Graph() if graph is None else graph

        for triple in self:
            _graph.add(triple)

        if not _graph:
            msg = f"Graph object '{_graph}' is empty. This might indicate an exhausted iterator."
            warnings.warn(msg)

        return _graph
