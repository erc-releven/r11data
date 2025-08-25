from typing import Literal as TypingLiteral

from rdflib import Namespace, URIRef

from lodkit import ClosedOntologyNamespace, NamespaceGraph, URIConstructorFactory
from r11data.tabular.main.utils.paths import ontologies_path


## for some reason, lodkit.ClosedOntologyNamespace does not load CRM
# crm = ClosedOntologyNamespace(ontology=ontologies_path / "crm.ttl")

crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig = ClosedOntologyNamespace(ontology=ontologies_path / "crmdig.ttl")

r11 = Namespace("https://r11.eu/rdf/resource/")
star = Namespace("https://r11.eu/ns/star/")
r11spec = Namespace("https://r11.eu/ns/spec/")
r11pros = Namespace("https://r11.eu/ns/prosopography/")

mkuri = URIConstructorFactory(r11)


class RelevenGraph(NamespaceGraph):
    crm = crm
    crmdig = crmdig

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
