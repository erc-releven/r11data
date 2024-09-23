"""Logging facilities for starlegs constructors."""

from collections import Counter
import io

from loguru import logger
from rdflib import Graph


def _starlegs_count_assertions(graph: Graph) -> dict[str, int]:
    c = Counter([p.rpartition("/")[-1] for p in graph.predicates()])
    return c


def _starlegs_create_count_log(count_mapping: dict[str, int], indent: int = 4) -> str:
    output = io.StringIO()

    for key, value in count_mapping.items():
        output.write(f"{' '*indent}{key}: {value}\n")

    return output.getvalue()


def starlegs_subgraph_log(subgraph: Graph, target_class: str):
    """Logger for intermediary starlegs graph results."""
    count_mapping = _starlegs_count_assertions(subgraph)

    _log_message = (
        f"Running starlegs constructor for {target_class} instances.\n"
        f"Generated {len(subgraph)} assertions:\n"
        f"{_starlegs_create_count_log(count_mapping=count_mapping)}"
    )

    logger.info(_log_message)


def starlegs_final_graph_log(graph: Graph):
    """Logger for final report on starlegs construction."""
    count_mapping = _starlegs_count_assertions(graph)

    _log_message = (
        f"Starlegs run finished generating {len(graph)} assertions:\n"
        f"{_starlegs_create_count_log(count_mapping=count_mapping)}"
    )

    logger.info(_log_message)