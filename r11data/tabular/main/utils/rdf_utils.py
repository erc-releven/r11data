from lodkit import ClosedOntologyNamespace, NamespaceGraph, URIConstructorFactory
from r11data.tabular.main.utils.paths import ontologies_path
from rdflib import Namespace


mkuri = URIConstructorFactory("https://r11.eu/ns/star/")

## for some reason, lodkit.ClosedOntologyNamespace does not load CRM
# crm = ClosedOntologyNamespace(ontology=ontologies_path / "crm.ttl")

crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig = ClosedOntologyNamespace(ontology=ontologies_path / "crmdig.ttl")


class RelevenGraph(NamespaceGraph):
    crm = crm
    crmdig = crmdig
