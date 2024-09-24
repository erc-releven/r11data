"""Runner for R11data starlegs generation."""

from SPARQLWrapper import SPARQLWrapper
from r11data import settings
from r11data.abcs import _ABCRunner
from r11data.starlegs.utils._types import CRMTemplateMap
from r11data.starlegs.utils.sparql_templates import p140_template_map, p141_template_map
from r11data.starlegs.utils.starlegs_logging import (
    starlegs_final_graph_log,
    starlegs_subgraph_log,
)
from r11data.utils.paths import output_starlegs
from rdflib import Graph


def starlegs(*template_maps: CRMTemplateMap) -> Graph:
    _graph = Graph()

    sparql = SPARQLWrapper("https://graphdb.r11.eu/repositories/RELEVEN")
    sparql.setCredentials(user=settings.GRAPHDB_USER, passwd=settings.PASSWD)

    for template_map in template_maps:
        for cls in template_map.crm_classes:
            query: str = template_map.sparql_construct_template.substitute(
                target_class=cls
            )

            sparql.setQuery(query=query)

            result_graph = sparql.queryAndConvert()
            starlegs_subgraph_log(subgraph=result_graph, target_class=cls)

            _graph += result_graph

    starlegs_final_graph_log(_graph)
    return _graph


class StarlegsRunner(_ABCRunner):
    """Runner for Starleg assertions."""

    def persist(self) -> None:
        """Run the conversion and persist the result in r11data/output."""
        graph = self.run()
        output_file = output_starlegs / "starlegs.ttl"

        with open(output_file, "w") as f:
            f.write(graph.serialize())

    def run(self) -> Graph:
        """Run the deaths table to RDF conversion."""
        graph = starlegs(p140_template_map, p141_template_map)
        return graph
