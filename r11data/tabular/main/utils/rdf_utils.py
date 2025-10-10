from typing import Literal as TypingLiteral

from lodkit import ClosedOntologyNamespace, NamespaceGraph, URIConstructorFactory
from r11data.utils.paths import ontologies_path
from rdflib import Namespace


crm = ClosedOntologyNamespace(ontology=ontologies_path / "crm.ttl")
crmdig = ClosedOntologyNamespace(ontology=ontologies_path / "crmdig.ttl")
lrm = ClosedOntologyNamespace(ontology=ontologies_path / "lrmoo.ttl")

r11 = Namespace("https://r11.eu/rdf/resource/")
star = Namespace("https://r11.eu/ns/star/")
r11spec = Namespace("https://r11.eu/ns/spec/")
r11pros = Namespace("https://r11.eu/ns/prosopography/")

mkuri = URIConstructorFactory(r11)

lewis_uri = mkuri("0009-0007-3535-6823")
aleks_uri = mkuri("0009-0007-1432-0127")


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
