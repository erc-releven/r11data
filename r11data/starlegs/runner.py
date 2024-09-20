"""Runner for R11data starlegs generation."""

import os

from SPARQLWrapper import SPARQLWrapper
from dotenv import load_dotenv
from r11data.starlegs.utils._types import CRMTemplateMap
from r11data.starlegs.utils.starlegs_logging import (
    starlegs_final_graph_log,
    starlegs_subgraph_log,
)
from rdflib import Graph

load_dotenv()
passwd = os.getenv("PASSWD")


def starlegs(*template_maps: CRMTemplateMap) -> Graph:
    _graph = Graph()

    sparql = SPARQLWrapper("https://graphdb.r11.eu/repositories/RELEVEN")
    sparql.setCredentials(user="admin", passwd=passwd)

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
