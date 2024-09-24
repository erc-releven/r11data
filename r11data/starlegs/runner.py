"""Runner for R11data starlegs generation."""

from collections.abc import Iterable
from itertools import chain
from typing import Iterator

from SPARQLWrapper import SPARQLWrapper
from r11data import settings
from r11data.abcs import _ABCRunner
from r11data.starlegs.utils._types import StarlegsQuery
from r11data.starlegs.utils.sparql_templates import p140_queries, p141_queries
from r11data.starlegs.utils.starlegs_logging import (
    starlegs_final_graph_log,
    starlegs_subgraph_log,
)
from r11data.utils.paths import output_starlegs
from rdflib import Graph


def starlegs(queries: Iterable[StarlegsQuery]) -> Graph:
    """Run starlegs construct queries and accumulate results into a Graph instance."""
    _graph = Graph()

    sparql = SPARQLWrapper("https://graphdb.r11.eu/repositories/RELEVEN")
    sparql.setCredentials(user=settings.GRAPHDB_USER, passwd=settings.PASSWD)

    for query in queries:
        _query: StarlegsQuery = query
        _target_class: str | None = query.metadata.get("target_class", None)

        sparql.setQuery(str(_query))
        result_graph = sparql.queryAndConvert()

        starlegs_subgraph_log(subgraph=result_graph, target_class=_target_class)
        _graph += result_graph

    starlegs_final_graph_log(_graph)
    return _graph


class StarlegsRunner(_ABCRunner):
    """Runner for Starleg assertions."""

    queries: Iterator[StarlegsQuery] = chain(p140_queries, p141_queries)

    def persist(self) -> None:
        """Run the conversion and persist the result in r11data/output."""
        graph = self.run()
        output_file = output_starlegs / "starlegs.ttl"

        with open(output_file, "w") as f:  # type: ignore
            f.write(graph.serialize())

    def run(self) -> Graph:
        """Run the deaths table to RDF conversion."""
        graph = starlegs(self.queries)
        return graph
