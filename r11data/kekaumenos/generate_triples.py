from collections.abc import Iterator
import itertools
import json

from lodkit import NamespaceGraph, URIConstructorFactory, _Triple, ttl
from r11data.utils.paths import output
from rdflib import Graph, Namespace, RDF, RDFS, URIRef


crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
so = Namespace("http://r11.eu/twc/ontologies/similarity/")

mkuri = URIConstructorFactory("https://r11.eu/ns/star/")
orcid_aleks = "https://orcid.org/0009-0007-1432-0127"


class KekaumenosGraph(NamespaceGraph):
    crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
    so = Namespace("http://r11.eu/twc/ontologies/similarity/")


def aleks_triples() -> Iterator[_Triple]:
    return ttl(
        mkuri(orcid_aleks),
        (RDF.type, crm.E21_Person),
        (RDFS.label, "Aleksandar Anđelović"),
        (
            crm.P1_is_identified_by,
            ttl(
                mkuri(f"e42_{orcid_aleks}"),
                (RDF.type, crm.E42_Identifier),
                (crm.P190_has_symbolic_content, orcid_aleks),
            ),
        ),
    )


def generate_relation_triples(data: dict) -> Iterator[_Triple]:
    return ttl(
        mkuri(),
        (RDF.type, crm.E13_Attribute_Assignment),
        (crm.P14_carried_out_by, mkuri(orcid_aleks)),
        (crm.P140_assigned_attribute_to, URIRef(data["r11_uri"])),
        (crm.P141_assigned, URIRef(data["saws_uri"])),
        (crm.P177_assigned_property_of_type, URIRef(so.ID5_related)),
    )


def generate_kekaumenos_graph() -> Graph:
    with open("./data/matches_selected_items.json") as f:
        json_data = json.load(f)

        triples = itertools.chain(
            *map(generate_relation_triples, json_data), aleks_triples()
        )

        graph = KekaumenosGraph()

        for triple in triples:
            graph.add(triple)

        return graph


def persist_kekaumenos_graph() -> None:
    kekaumenos_graph: Graph = generate_kekaumenos_graph()
    kekaumenos_path = output / "kekaumenos/kekaumenos_graph.ttl"

    with open(kekaumenos_path, "w") as f:  # type: ignore
        f.write(kekaumenos_graph.serialize())


persist_kekaumenos_graph()
