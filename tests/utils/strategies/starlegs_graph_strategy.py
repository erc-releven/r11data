"""Hypothesis strategy for Starleg testing graph generation"""

from string import Template
from typing import Annotated

import hypothesis.strategies as st
from hypothesis.strategies._internal.strategies import SearchStrategy
from lodkit import _Triple
from r11data.starlegs.utils.sparql_templates import _p140_crm_classes
from rdflib import Graph, Namespace, URIRef


crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


_base_graph: str = """
@prefix crm: <http://www.cidoc-crm.org/cidoc-crm/> .
@prefix sdhss: <https://r11.eu/ns/prosopography/> .
@prefix star: <https://r11.eu/ns/star/> .

star:64db5be9-f51a-4c50-822a-8b115ff69161 a star:$target_class ;
    crm:P140_assigned_attribute_to star:common ;
    crm:P141_assigned star:38a81e87e7 ;
    crm:P14_carried_out_by <urn:agent> ;
    crm:P17_was_motivated_by <urn:source> .

<urn:e13_a2> a star:E13_crm_P4 ;
    crm:P140_assigned_attribute_to star:common ;
    crm:P141_assigned star:168c6c9257 .

<urn:e13_a3> a star:E13_crm_P42 ;
    crm:P140_assigned_attribute_to star:common ;
    crm:P141_assigned star:f4baf901d1 .
"""

base_graph_template = Template(_base_graph)

starlegs_triples: list[_Triple] = [
    (URIRef("urn:e13_a2"), crm.P14_carried_out_by, URIRef("urn:agent")),
    (URIRef("urn:e13_a2"), crm.P17_was_motivated_by, URIRef("urn:source")),
    (URIRef("urn:e13_a3"), crm.P14_carried_out_by, URIRef("urn:agent")),
    (URIRef("urn:e13_a3"), crm.P17_was_motivated_by, URIRef("urn:source")),
]

starlegs_predicate_object_strategy: Annotated[
    SearchStrategy[list[_Triple]],
    "Generate a list of 0-4 starlegs triples for adding to the test graph.",
] = st.lists(st.sampled_from(starlegs_triples), min_size=0, max_size=4, unique=True)

target_classes: list[str] = _p140_crm_classes
starlegs_target_class_strategy: Annotated[
    SearchStrategy[str], "Strategy for retrieving a crm target class from."
] = st.sampled_from(target_classes)


def generate_starlegs_graph(
    target_class: str, starlegs_triples: list[_Triple]
) -> Graph:
    """Generate a test graph based on a target class and starlegs_triples."""
    _graph_data = base_graph_template.substitute(target_class=target_class)
    graph = Graph().parse(data=_graph_data, format="ttl")

    for triple in starlegs_triples:
        graph.add(triple)

    return graph


starlegs_graph_strategy: Annotated[
    SearchStrategy[Graph],
    "Strategy for generating a Graph with starlegs randomly missing.",
] = st.builds(
    generate_starlegs_graph,
    target_class=starlegs_target_class_strategy,
    starlegs_triples=starlegs_predicate_object_strategy,
)
