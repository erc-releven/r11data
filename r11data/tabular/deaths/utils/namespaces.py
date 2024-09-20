"""RDFLib Namespaces and Namespacemanager for R11."""

import sys

from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager


crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
star = Namespace("https://r11.eu/ns/star/")
sd = Namespace("https://r11.eu/rdf/resource/")
lrmoo = Namespace("http://iflastandards.info/ns/lrm/lrmoo/")
crmdig = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
rdfg = Namespace("http://www.w3.org/2009/rdfg#")


_namespaces = {
    key: value
    for key, value in sys.modules[__name__].__dict__.items()
    if isinstance(value, Namespace)
}


class R11NamespaceManager(NamespaceManager):
    """Custom NamespaceManager for R11.

    Useage e.g. for creating a namespaced graph:
    ```
    graph = rdflib.Graph
    R11NamespaceManager(graph)
    ```
    """

    def __init__(self, graph: Graph, bind_namespaces="rdflib"):
        """Call init.super and add CLSInfra namespaces."""
        super().__init__(graph=graph, bind_namespaces=bind_namespaces)

        for prefix, ns in _namespaces.items():
            graph.bind(prefix, ns)
